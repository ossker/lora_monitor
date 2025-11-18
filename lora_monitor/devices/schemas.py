from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# --- MODELE DLA RX METADATA ---
class GatewayIDs(BaseModel):
    gateway_id: Optional[str] = None
    eui: Optional[str] = None
    model_config = {"extra": "allow"}

class Location(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    source: Optional[str] = None
    model_config = {"extra": "allow"}

class RxMetadata(BaseModel):
    gateway_ids: Optional[GatewayIDs] = None
    time: Optional[str] = None
    timestamp: Optional[int] = None
    rssi: Optional[int] = None
    channel_rssi: Optional[int] = None
    snr: Optional[float] = None
    location: Optional[Location] = None
    uplink_token: Optional[str] = None
    channel_index: Optional[int] = None
    received_at: Optional[str] = None
    model_config = {"extra": "allow"}

# --- MODELE DLA UPLINK MESSAGE ---
class UplinkMessage(BaseModel):
    f_port: Optional[int] = None
    f_cnt: Optional[int] = None
    frm_payload: Optional[str] = None
    decoded_payload: Optional[Dict[str, float]] = None
    rx_metadata: Optional[List[RxMetadata]] = None
    settings: Optional[Dict] = None
    received_at: Optional[str] = None
    consumed_airtime: Optional[str] = None
    network_ids: Optional[Dict[str, str]] = None
    model_config = {"extra": "allow"}

# --- END DEVICE IDS ---
class EndDeviceIDs(BaseModel):
    device_id: Optional[str] = None
    application_ids: Optional[Dict[str, str]] = None
    dev_eui: Optional[str] = None
    dev_addr: Optional[str] = None
    model_config = {"extra": "allow"}

# --- DANE GŁÓWNE ---
class DataField(BaseModel):
    type_: Optional[str] = Field(None, alias='@type')
    end_device_ids: Optional[EndDeviceIDs] = None
    correlation_ids: Optional[List[str]] = None
    received_at: Optional[str] = None
    uplink_message: Optional[UplinkMessage] = None
    model_config = {"extra": "allow"}

class DeviceIDs(BaseModel):
    device_ids: Optional[EndDeviceIDs] = None
    model_config = {"extra": "allow"}

class TTNWebhook(BaseModel):
    name: Optional[str] = None
    time: Optional[str] = None
    identifiers: Optional[List[DeviceIDs]] = None
    data: Optional[DataField] = None
    correlation_ids: Optional[List[str]] = None
    origin: Optional[str] = None
    context: Optional[Dict[str, str]] = None
    visibility: Optional[Dict[str, List[str]]] = None
    unique_id: Optional[str] = None
    model_config = {"extra": "allow"}
