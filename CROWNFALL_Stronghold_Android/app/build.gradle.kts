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
        versionCode = 23
        versionName = "0.23"
        manifestPlaceholders["appLabel"] = "CROWNFALL: Stronghold"
    }

    flavorDimensions += "channel"
    productFlavors {
        create("compat") {
            dimension = "channel"
            applicationIdSuffix = ".preview023"
            versionNameSuffix = "-preview"
            targetSdk = 35
            signingConfig = signingConfigs.getByName("debug")
            manifestPlaceholders["appLabel"] = "CROWNFALL TEST 0.23"
        }
        create("play") {
            dimension = "channel"
            targetSdk = 36
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
