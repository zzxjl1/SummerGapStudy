
-keep class android.view.** { *; }
-dontwarn android.support.v8.renderscript.**
-keep public class android.support.v8.renderscript.** { *; }
-dontwarn androidx.renderscript.**
-keep class androidx.renderscript.** { *; }

-keep class com.kongzue.baseokhttp.** { *; }
-keepclassmembers class * extends android.webkit.WebChromeClient{
    public void openFileChooser(...);
}