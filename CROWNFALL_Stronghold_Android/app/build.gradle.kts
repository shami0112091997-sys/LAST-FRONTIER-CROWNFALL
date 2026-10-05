plugins {
    id("com.android.application")
}

android {
    namespace = "com.crownfall.stronghold"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.crownfall.stronghold"
        minSdk = 23
        targetSdk = 35
        versionCode = 24
        versionName = "0.24"
        manifestPlaceholders["appLabel"] = "CROWNFALL: Stronghold"
    }

    flavorDimensions += "channel"
    productFlavors {
        create("compat") {
            dimension = "channel"
            applicationIdSuffix = ".preview024"
            versionNameSuffix = "-preview"
            targetSdk = 35
            manifestPlaceholders["appLabel"] = "CROWNFALL TEST 0.24"
        }
        create("play") {
            dimension = "channel"
            targetSdk = 35
            manifestPlaceholders["appLabel"] = "CROWNFALL: Stronghold"
        }
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
        }
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
