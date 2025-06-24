@file:Suppress("unused")

package top.lgc2333.sleppy_rework.types

import de.jensklingenberg.ktorfit.http.Body
import de.jensklingenberg.ktorfit.http.DELETE
import de.jensklingenberg.ktorfit.http.GET
import de.jensklingenberg.ktorfit.http.Headers
import de.jensklingenberg.ktorfit.http.PATCH
import de.jensklingenberg.ktorfit.http.PUT
import de.jensklingenberg.ktorfit.http.Path

interface SleepyReworkApi {
  @GET("api/v1") suspend fun testAlive(): String

  @GET("api/v1/config/frontend") suspend fun getFrontendConfig(): FrontendConfig

  @GET("api/v1/info") suspend fun getInfo(): Info

  @GET("api/v1/device/{deviceKey}/config")
  suspend fun getDeviceConfig(@Path deviceKey: String): DeviceConfig

  @PUT("api/v1/device/{deviceKey}/config")
  suspend fun putDeviceConfig(@Path deviceKey: String, @Body config: DeviceConfig): OpSuccess

  @PUT("api/v1/device/{deviceKey}/config")
  suspend fun putDeviceConfig(@Path deviceKey: String, @Body config: String): OpSuccess

  @Headers("Content-Type: application/json")
  @PATCH("api/v1/device/{deviceKey}/info")
  suspend fun patchDeviceInfo(
    @Path deviceKey: String,
    @Body info: DeviceInfoFromClient? = null,
  ): DeviceInfo

  @Headers("Content-Type: application/json")
  @PATCH("api/v1/device/{deviceKey}/info")
  suspend fun patchDeviceInfo(@Path deviceKey: String, @Body info: String): DeviceInfo

  @Headers("Content-Type: application/json")
  @PUT("api/v1/device/{deviceKey}/info")
  suspend fun putDeviceInfo(
    @Path deviceKey: String,
    @Body info: DeviceInfoFromClient? = null,
  ): DeviceInfo

  @Headers("Content-Type: application/json")
  @PUT("api/v1/device/{deviceKey}/info")
  suspend fun putDeviceInfo(@Path deviceKey: String, @Body info: String): DeviceInfo

  @DELETE("api/v1/device/{deviceKey}/info")
  suspend fun deleteDeviceInfo(@Path deviceKey: String): OpSuccess
}
