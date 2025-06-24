import org.jetbrains.kotlin.gradle.ExperimentalKotlinGradlePluginApi
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
  alias(libs.plugins.kotlinMultiplatform)
  alias(libs.plugins.androidLibrary)
  // alias(libs.plugins.vanniktech.mavenPublish)

  alias(libs.plugins.serialization)
  alias(libs.plugins.ksp)
  alias(libs.plugins.ktorfit)
}

group = "top.lgc2333.sleppy_rework"

version = "0.1.0"

kotlin {
  jvm()
  androidTarget {
    publishLibraryVariants("release")
    @OptIn(ExperimentalKotlinGradlePluginApi::class)
    compilerOptions { jvmTarget.set(JvmTarget.JVM_11) }
  }
  iosX64()
  iosArm64()
  iosSimulatorArm64()
  linuxX64()

  sourceSets {
    val commonMain by getting {
      dependencies {
        implementation(libs.ktorfit.lib)
        implementation(libs.ktor.client.auth)
        implementation(libs.ktor.client.content.negotiation)
        implementation(libs.ktor.serialization.kotlinx.json)
      }
    }
    val commonTest by getting {
      dependencies {
        implementation(libs.kotlin.test)
        implementation(libs.kotlin.test.common)
        implementation(libs.ktor.client.cio)
      }
    }
    val jvmMain by getting { dependencies { implementation(libs.slf4j.nop) } }
  }
}

android {
  namespace = group.toString()
  compileSdk = libs.versions.android.compileSdk.get().toInt()
  defaultConfig { minSdk = libs.versions.android.minSdk.get().toInt() }
  compileOptions {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
  }
}

tasks.configureEach {
  if (
    name.startsWith("kspKotlin") ||
      name == "kspDebugKotlinAndroid" ||
      name == "kspReleaseKotlinAndroid"
  ) {
    dependsOn("kspCommonMainKotlinMetadata")
  }
}

// mavenPublishing {
//   publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL)
//
//   signAllPublications()
//
//   coordinates(group.toString(), "library", version.toString())
//
//   pom {
//     name = "Sleepy Rework Types"
//     description = ""
//     inceptionYear = "2025"
//     url = ""
//     licenses {
//       license {
//         name = "XXX"
//         url = "YYY"
//         distribution = "ZZZ"
//       }
//     }
//     developers {
//       developer {
//         id = "XXX"
//         name = "YYY"
//         url = "ZZZ"
//       }
//     }
//     scm {
//       url = "XXX"
//       connection = "YYY"
//       developerConnection = "ZZZ"
//     }
//   }
// }
