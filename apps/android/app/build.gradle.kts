plugins {
    id("com.android.application")
}

android {
    namespace = "dev.qbt.mobile"
    compileSdk = 36

    defaultConfig {
        applicationId = "dev.qbt.mobile"
        minSdk = 26
        targetSdk = 36
        versionCode = 4
        versionName = "0.4.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
}
