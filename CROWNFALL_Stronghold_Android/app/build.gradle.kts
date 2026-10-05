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
        versionCode = 9
        versionName = "0.9"
    }

    buildTypes {
        debug { isMinifyEnabled = false }
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
