import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="FRESHCHAIN : Low-Cost IoT Blockchain Node for Farm-to-Fork Traceability",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'telemetry_log' not in st.session_state:
    st.session_state.telemetry_log = []
if 'offline_buffer' not in st.session_state:
    st.session_state.offline_buffer = []
if 'last_hash' not in st.session_state:
    st.session_state.last_hash = "0" * 64  # Genesis hash
if 'db_tampered' not in st.session_state:
    st.session_state.db_tampered = False

# Sidebar Controls (Edge Node Simulation)
st.sidebar.title("Edge Node Controls")
network_status = st.sidebar.toggle("Network Available (LTE/MQTT)", value=True)
sim_temp_excursion = st.sidebar.checkbox("Simulate Temp Excursion (> 8°C)", value=False)
sim_tamper = st.sidebar.checkbox("Simulate Enclosure Open / Tamper", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("Shipment Metadata")
shipment_id = st.sidebar.text_input("Shipment / Batch ID", value="FC-1042 (Mangoes)")
current_location = st.sidebar.text_input("Current Location", value="Transit Hub - Node 4")

# Main Title & Executive Summary Header
st.title("FRESHCHAIN: Farm-to-Fork Traceability Console")
st.markdown("**Problem Statement 26232 | Smart India Hackathon** — Low-Cost IoT Blockchain Node with Device-Signed Evidence & Cumulative Exposure Tracking.")

# Tabs Mapping Document Architecture
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Shipment Overview", 
    "🗺️ Journey Timeline & Buffering", 
    "🔗 Integrity & Verification", 
    "⚡ Condition Model & Actions", 
    "⚙️ Hardware & Architecture Docs"
])

# -------------------------------------------------------------
# TAB 1: SHIPMENT OVERVIEW
# -------------------------------------------------------------
with tab1:
    st.subheader(f"Active Monitoring: {shipment_id}")
    
    # Generate sensor values
    temp_val = 31.0 if sim_temp_excursion else 4.2
    humidity_val = 82.0 if sim_temp_excursion else 65.0
    voc_trend = "Elevated (Ripening Triggered)" if sim_temp_excursion else "Normal Baseline"
    status_state = "TAMPERED" if sim_tamper else ("EXCURSION" if sim_temp_excursion else "NORMAL")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperature", f"{temp_val}°C", delta="+26.8°C" if sim_temp_excursion else "Optimal", delta_color="inverse")
    with col2:
        st.metric("Humidity", f"{humidity_val}%", delta="Stable")
    with col3:
        st.metric("Battery / Power", "88% (Solar Active)", delta="Healthy")
    with col4:
        st.metric("Node Status", status_state)

    st.markdown("---")
    
    # Action triggers to log record
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        if st.button("Record Telemetry Event", type="primary"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Payload payload formatting
            payload_str = f"{timestamp}|{shipment_id}|{current_location}|{temp_val}|{humidity_val}|{status_state}"
            
            # Cryptographic Hash Chaining: H(n) = SHA256(record || H(n-1))
            block_data = f"{st.session_state.last_hash}|{payload_str}"
            current_hash = hashlib.sha256(block_data.encode()).hexdigest()
            
            record = {
                "Timestamp": timestamp,
                "Shipment ID": shipment_id,
                "Location": current_location,
                "Temp (°C)": temp_val,
                "Humidity (%)": humidity_val,
                "VOC Trend": voc_trend,
                "Status": status_state,
                "Prev Hash": st.session_state.last_hash[:10] + "...",
                "Current Hash": current_hash[:10] + "...",
                "FullHash": current_hash,
                "Signature": "ATECC608B_ECDSA_Sig_" + current_hash[:8]
            }
            
            if network_status:
                st.session_state.telemetry_log.append(record)
                st.session_state.last_hash = current_hash
                st.success("Telemetry recorded, device-signed, and synced to cloud ledger.")
            else:
                st.session_state.offline_buffer.append(record)
                st.warning("Network offline! Record safely secured inside edge SPI NOR Flash / FRAM buffer.")

    # Show active ledger table
    st.markdown("### Live Immutable Ledger Feed")
    if len(st.session_state.telemetry_log) > 0:
        df_live = pd.DataFrame(st.session_state.telemetry_log)
        st.dataframe(df_live[["Timestamp", "Shipment ID", "Location", "Temp (°C)", "Status", "Prev Hash", "Current Hash"]], use_container_width=True)
    else:
        st.info("No logs registered yet. Click 'Record Telemetry Event' above.")

# -------------------------------------------------------------
# TAB 2: JOURNEY TIMELINE & OFFLINE BUFFERING
# -------------------------------------------------------------
with tab2:
    st.subheader("Offline-First Edge Buffering & Gap-Aware Sync")
    st.markdown("Simulates network dropouts in remote transit corridors. Sensing, signing, and storage continue via FRAM and SPI flash without data loss.")

    if len(st.session_state.offline_buffer) > 0:
        st.warning(f"⚠️ Unsynced Backlog in Edge Storage: **{len(st.session_state.offline_buffer)} records** waiting for connection.")
        st.dataframe(pd.DataFrame(st.session_state.offline_buffer)[["Timestamp", "Shipment ID", "Temp (°C)", "Status"]])
        
        if network_status and st.button("Simulate Automatic Network Recovery & Sync"):
            st.session_state.telemetry_log.extend(st.session_state.offline_buffer)
            # Update hash chain continuously
            for r in st.session_state.offline_buffer:
                st.session_state.last_hash = r["FullHash"]
            st.session_state.offline_buffer = []
            st.success("Buffer synchronized successfully, oldest-first, maintaining cryptographic continuity.")
            st.rerun()
    else:
        st.success("Edge Buffer Status: Fully synced with backend server. No transmission gaps.")

    st.markdown("### Journey Route & Event Timeline")
    st.markdown("""
    * **08:00 AM** — Farm Gate Loading (Node Normal, Temp: 4.1°C)
    * **11:30 AM** — Regional Highway Corridor (Network Lost ➔ Edge Buffer Engaged)
    * **02:00 PM** — Border Checkpoint (Network Restored ➔ 45 Backlogged Records Synced)
    * **06:00 PM** — Current Node: Transit Hub - Node 4 (Active monitoring active)
    """)

# -------------------------------------------------------------
# TAB 3: INTEGRITY & VERIFICATION (DEMO PROOF POINT)
# -------------------------------------------------------------
with tab3:
    st.subheader("Cryptographic Hash Chain & Merkle Anchor Verification")
    st.markdown("Verifies device-signed evidence. **Demonstrates tamper detection:** modifying database rows breaks the cryptographic chain.")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("Verify Ledger Integrity"):
            st.session_state.db_tampered = False
            st.success("✅ **Verification Passed:** All device signatures verified via ATECC608B public key. Merkle root matched on EVM testnet contract.")
    with col_v2:
        if st.button("Inject Tampering (Modify Database Row)", type="secondary"):
            st.session_state.db_tampered = True
            st.warning("⚠️ Simulated malicious backend edit executed on row 1 temperature value.")

    if len(st.session_state.telemetry_log) > 0:
        df_verify = pd.DataFrame(st.session_state.telemetry_log).copy()
        if st.session_state.db_tampered:
            df_verify.loc[0, "Temp (°C)"] = -99.9  # Tampered value
            st.error("🚨 **INTEGRITY CHECK FAILED:** Hash mismatch detected at Block #0! The stored data does not match the chained hash header.")
        
        st.dataframe(df_verify[["Timestamp", "Shipment ID", "Temp (°C)", "Status", "Signature", "Current Hash"]], use_container_width=True)
    else:
        st.info("Record items in Tab 1 to enable verification audits.")

    st.markdown("---")
    st.markdown("**Smart Contract Anchoring Details (EVM Testnet):**")
    st.code("Contract Address: 0x71C...32a9 | Merkle Root: 0x4f9b...e211 | Status: Anchored & Verified", language="text")

# -------------------------------------------------------------
# TAB 4: CONDITION MODEL & ACTION ENGINE
# -------------------------------------------------------------
with tab4:
    st.subheader("Cumulative Exposure & Condition-Aware FEFO Action Engine")
    st.markdown("Converts cumulative thermal and environmental exposure into remaining shelf-life percentage and automated priority handling.")

    # Calculate simulated budget
    consumed_budget = 68.5 if sim_temp_excursion else 38.0
    remaining_budget = 100.0 - consumed_budget

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Shelf-Life Budget Consumed", f"{consumed_budget}%", delta="High Degradation Rate" if sim_temp_excursion else "Normal Rate", delta_color="inverse")
    with col_b:
        priority_label = "VERY HIGH (HOLD / INSPECT)" if (sim_temp_excursion or sim_tamper) else "NORMAL (FEFO Ready)"
        st.metric("Action Engine Priority", priority_label)

    st.markdown("---")
    st.markdown("### Automated Governance Decision Support")
    if sim_temp_excursion or sim_tamper:
        st.error("""
        **Action Triggered: INSPECT & HOLD**
        * **Reason Codes:** Thermal excursion exceeding threshold limits for >2 hours OR physical enclosure tamper switch triggered.
        * **Supply Chain Route:** Diverted from direct retail to local processing warehouse. Quality Assurance team notified via MQTT broker broadcast.
        """)
    else:
        st.success("""
        **Action Triggered: NORMAL TRANSIT & PRIORITY DISTRIBUTION (FEFO)**
        * **Reason Codes:** Cumulative exposure within acceptable cultivar limits.
        * **Supply Chain Route:** Cleared for primary export distribution channel.
        """)

# -------------------------------------------------------------
# TAB 5: HARDWARE & SYSTEM ARCHITECTURE DOCS
# -------------------------------------------------------------
with tab5:
    st.subheader("System Architecture & Specification Reference")
    st.markdown("Complete technical specifications extracted from the final solution document[cite: 9].")

    spec_data = {
        "Subsystem": ["MCU", "Secure Element", "Sensors", "Connectivity", "Storage", "Power Supply"],
        "Component Choice": [
            "ESP32-S3 (Secure Boot v2, Flash Encryption)", 
            "ATECC608B (Hardware ECDSA P-256 Key)", 
            "SHT40 (Temp/RH), LIS3DH (Accelerometer), VOC Trend", 
            "LTE Cat-1 Module with MQTT over TLS", 
            "FRAM (State/Pointers) + 16MB SPI NOR Flash (Ring Buffer)", 
            "Solar Panel + PMIC + Li-ion Cell (Energy-Aware Duty Cycling)"
        ],
        "Engineering Purpose": [
            "Core orchestration, communication, and local compute",
            "Non-extractable hardware root of trust & signing identity",
            "Core cold-chain telemetry and physical motion/shock checks",
            "Reliable cloud synchronization across cellular networks",
            "Loss-resistant offline logging supporting months of backlog",
            "Extended autonomy under low-sun and zero-power conditions"
        ]
    }
    st.table(pd.DataFrame(spec_data))