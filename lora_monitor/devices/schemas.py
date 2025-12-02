from pydantic import BaseModel, Field
from typing import List, Optional


class GatewayIDs(BaseModel):
    gateway_id: str
    eui: Optional[str] = None


class Location(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    source: str


class RxMetadata(BaseModel):
    gateway_ids: GatewayIDs
    time: Optional[str] = None
    timestamp: Optional[int] = None
    rssi: Optional[float] = None
    channel_rssi: Optional[float] = None
    snr: Optional[float] = None
    location: Optional[Location] = None
    uplink_token: Optional[str] = None
    channel_index: Optional[int] = None
    received_at: Optional[str] = None


class LoraSettings(BaseModel):
    bandwidth: int
    spreading_factor: int
    coding_rate: str


class DataRate(BaseModel):
    lora: LoraSettings


class UplinkSettings(BaseModel):
    data_rate: DataRate
    frequency: str
    timestamp: int
    time: Optional[str] = None


class NetworkIDs(BaseModel):
    net_id: str
    ns_id: str
    tenant_id: str
    cluster_id: str
    cluster_address: str


class DecodedPayload(BaseModel):
    temperature_1: float
    relative_humidity_2: float
    barometric_pressure_3: float


class UplinkMessage(BaseModel):
    f_port: int
    f_cnt: int
    frm_payload: str
    decoded_payload: Optional[DecodedPayload] = None
    rx_metadata: List[RxMetadata]
    settings: UplinkSettings
    received_at: str
    consumed_airtime: str
    network_ids: NetworkIDs


class ApplicationIDs(BaseModel):
    application_id: str


class EndDeviceIDs(BaseModel):
    device_id: str
    application_ids: ApplicationIDs
    dev_eui: str
    dev_addr: str


class DataField(BaseModel):
    type_: str = Field(..., alias='@type')
    end_device_ids: EndDeviceIDs
    correlation_ids: List[str]
    received_at: str
    uplink_message: UplinkMessage


class DeviceIDs(BaseModel):
    device_ids: EndDeviceIDs


class Visibility(BaseModel):
    rights: List[str]


class Context(BaseModel):
    tenant_id: str = Field(..., alias='tenant-id')


class TTNWebhook(BaseModel):
    name: str
    time: str
    identifiers: List[DeviceIDs]
    data: DataField
    correlation_ids: List[str]
    origin: str
    context: Context
    visibility: Visibility
    unique_id: str
