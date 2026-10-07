plugins {
    id("com.android.application")
}

val releaseKeystore = System.getenv("CROWNFALL_KEYSTORE_FILE")
val releaseStorePassword = System.getenv("CROWNFALL_KEYSTORE_PASSWORD")
val releaseKeyAlias = System.getenv("CROWNFALL_KEY_ALIAS")
val releaseKeyPassword = System.getenv("CROWNFALL_KEY_PASSWORD")
val hasReleaseSigning = !releaseKeystore.isNullOrBlank() &&
    !releaseStorePassword.isNullOrBlank() &&
    !releaseKeyAlias.isNullOrBlank() &&
    !releaseKeyPassword.isNullOrBlank()

android {
    namespace = "com.crownfall.stronghold"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.crownfall.stronghold"
        minSdk = 23
        targetSdk = 36
        versionCode = 214
        versionName = "2.1.2"
        manifestPlaceholders["appLabel"] = "CROWNFALL: Stronghold"
    }

    if (hasReleaseSigning) {
        signingConfigs {
            create("release") {
                storeFile = file(releaseKeystore!!)
                storePassword = releaseStorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
                enableV1Signing = true
                enableV2Signing = true
                enableV3Signing = true
            }
        }
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
        }
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            if (hasReleaseSigning) {
                signingConfig = signingConfigs.getByName("release")
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
