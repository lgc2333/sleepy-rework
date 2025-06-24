@file:Suppress("unused")

package top.lgc2333.sleppy_rework.types

import io.ktor.client.statement.HttpResponse
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.decodeFromJsonElement

const val VERSION = "0.1.0"

fun createDefaultJson() = Json { ignoreUnknownKeys = true }

inline fun <reified T> JsonElement.decode(json: Json? = null): T? =
  (json ?: createDefaultJson()).decodeFromJsonElement<T>(this)

@Suppress("CanBeParameter")
class APIException(var response: HttpResponse, var detail: ErrDetail) :
  Exception(
    "[${response.status.value} ${response.status.description}]" +
      (if (detail.type != null) " (${detail.type})" else "") +
      (if (detail.msg != null) " ${detail.msg}" else "")
  )

@Serializable
enum class DeviceType(val value: String) {
  @SerialName("pc") PC("pc"),
  @SerialName("laptop") LAPTOP("laptop"),
  @SerialName("phone") PHONE("phone"),
  @SerialName("tablet") TABLET("tablet"),
  @SerialName("smartwatch") SMARTWATCH("smartwatch"),
  @SerialName("") UNKNOWN(""),
}

@Serializable
enum class OnlineStatus(val value: String) {
  @SerialName("online") ONLINE("online"),
  @SerialName("offline") OFFLINE("offline"),
  @SerialName("idle") IDLE("idle"),
  @SerialName("unknown") UNKNOWN("unknown"),
}

@Serializable
data class ErrDetail(
  var type: String? = null,
  var msg: String? = null,
  var data: JsonElement? = null,
)

@Serializable data class WSErr(var code: Int, var detail: ErrDetail)

@Serializable
data class PydanticErrorDetail(
  var type: String,
  var loc: List<JsonPrimitive>,
  var msg: String,
  var input: JsonElement,
  var ctx: Map<String, JsonObject>? = null,
  var url: String? = null,
)

@Serializable
data class OpSuccess(
  /** Always to true */
  var success: Boolean = true
)

@Serializable
data class FrontendStatusConfig(var name: String, var description: String, var color: String)

@Serializable
data class FrontendConfig(var username: String, var statuses: Map<String, FrontendStatusConfig>)

@Serializable
data class DeviceCurrentApp(
  var name: String? = null,
  /** 13 digits timestamp */
  @SerialName("last_change_time") var lastChangeTime: Long? = null,
)

@Serializable
data class DeviceBatteryStatus(
  var percent: Int? = null,
  /** in seconds */
  @SerialName("time_left") var timeLeft: Int? = null,
  var charging: Boolean = false,
)

@Serializable
data class DeviceData(
  @SerialName("current_app") var currentApp: DeviceCurrentApp? = null,
  var battery: DeviceBatteryStatus? = null,
  @SerialName("additional_statuses") var additionalStatuses: List<String>? = null,
)

@Serializable
data class DeviceConfig(
  var name: String = "Unnamed Device",
  var description: String? = null,
  @SerialName("device_type") var deviceType: DeviceType? = null,
  @SerialName("device_os") var deviceOS: String? = null,
  @SerialName("remove_when_offline") var removeWhenOffline: Boolean = false,
)

@Serializable
data class DeviceInfoFromClient(
  var name: String = "Unnamed Device",
  var description: String? = null,
  @SerialName("device_type") var deviceType: String? = null,
  @SerialName("device_os") var deviceOS: String? = null,
  @SerialName("remove_when_offline") var removeWhenOffline: Boolean = false,
  var idle: Boolean = false,
  var data: DeviceData? = null,
)

@Serializable
data class DeviceInfoFromClientWS(
  var name: String = "Unnamed Device",
  var description: String? = null,
  @SerialName("device_type") var deviceType: String? = null,
  @SerialName("device_os") var deviceOS: String? = null,
  @SerialName("remove_when_offline") var removeWhenOffline: Boolean = false,
  var idle: Boolean = false,
  var data: DeviceData? = null,
  var replace: Boolean = false,
)

@Serializable
data class DeviceInfo(
  var name: String = "Unnamed Device",
  var description: String? = null,
  @SerialName("device_type") var deviceType: String? = null,
  @SerialName("device_os") var deviceOS: String? = null,
  @SerialName("remove_when_offline") var removeWhenOffline: Boolean = false,
  var idle: Boolean = false,
  var data: DeviceData? = null,
  var online: Boolean = false,
  /** 13 digits timestamp */
  @SerialName("last_update_time") var lastUpdateTime: Long? = null,
  @SerialName("long_connection") var longConnection: Boolean = false,
)

@Serializable
data class Info(var status: OnlineStatus, var devices: Map<String, DeviceInfo>? = null)
