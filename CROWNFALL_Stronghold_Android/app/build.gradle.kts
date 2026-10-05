plugins {
    id("com.android.application")
}

android {
    namespace = "com.crownfall.stronghold"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.crownfall.stronghold"
        minSdk = 24
        targetSdk = 36
        versionCode = 11
        versionName = "0.11"
        manifestPlaceholders["appLabel"] = "CROWNFALL: Stronghold"
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
            applicationIdSuffix = ".test"
            versionNameSuffix = "-test"
            manifestPlaceholders["appLabel"] = "CROWNFALL DEBUG"
        }
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
        create("preview") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            applicationIdSuffix = ".preview011"
            versionNameSuffix = "-preview"
            isDebuggable = false
            isMinifyEnabled = false
            manifestPlaceholders["appLabel"] = "CROWNFALL TEST 0.11"
            matchingFallbacks += listOf("release")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
