@file:Suppress("unused")

package top.lgc2333.sleppy_rework.types

import de.jensklingenberg.ktorfit.Ktorfit
import io.ktor.client.HttpClient
import io.ktor.client.HttpClientConfig
import io.ktor.client.call.body
import io.ktor.client.engine.HttpClientEngineConfig
import io.ktor.client.engine.HttpClientEngineFactory
import io.ktor.client.plugins.UserAgent
import io.ktor.client.plugins.api.createClientPlugin
import io.ktor.client.plugins.auth.Auth
import io.ktor.client.plugins.auth.providers.BearerTokens
import io.ktor.client.plugins.auth.providers.bearer
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json

val ClientPlugin =
  createClientPlugin("SleepyReworkClientPlugin") {
    onResponse { response ->
      if (response.status.value < 200 || response.status.value >= 300) {
        throw APIException(response, response.body<ErrDetail>())
      }
    }
  }

fun <T : HttpClientEngineConfig> createApi(
  baseUrl: String,
  secret: String? = null,
  engineFactory: HttpClientEngineFactory<T>? = null,
  json: Json? = null,
  appUserAgent: String? = null,
  clientConfigureBlock: (HttpClientConfig<*>.() -> Unit)? = null,
  builderConfigureBlock: (Ktorfit.Builder.() -> Unit)? = null,
): SleepyReworkApi {
  val json = json ?: createDefaultJson()
  val block: HttpClientConfig<*>.() -> Unit = {
    if (secret != null) {
      install(Auth) { bearer { BearerTokens(secret, null) } }
    }
    install(UserAgent) {
      agent =
        "ktor-client sleepy-rework-types/${VERSION} (Kotlin)" +
          if (!appUserAgent.isNullOrBlank()) " $appUserAgent" else ""
    }
    install(ClientPlugin)
    install(ContentNegotiation) { json(json) }
    clientConfigureBlock?.invoke(this)
  }
  val client = if (engineFactory == null) HttpClient(block) else HttpClient(engineFactory, block)
  return Ktorfit.Builder()
    .baseUrl(if (baseUrl.endsWith('/')) baseUrl else "${baseUrl}/")
    .httpClient(client)
    .apply { builderConfigureBlock?.invoke(this) }
    .build()
    .createSleepyReworkApi()
}
