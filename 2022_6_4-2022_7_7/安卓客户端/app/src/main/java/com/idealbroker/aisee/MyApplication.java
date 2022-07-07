package com.idealbroker.aisee;


import android.app.Activity;
import android.app.Application;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.kongzue.baseokhttp.util.BaseOkHttp;
import com.kongzue.dialogx.DialogX;
import com.kongzue.dialogx.style.IOSStyle;
import com.tencent.tauth.Tencent;

import org.opencv.android.OpenCVLoader;


public class MyApplication extends Application {
    public static MyApplication context;
    public static Tencent mTencent;
    public static User user;
    public static TTS tts;
    public static SharedPreferences settings;
    private int count = 0;

    @Override
    public void onCreate() {
        super.onCreate();
        context = this;
        settings = PreferenceManager.getDefaultSharedPreferences(this);
        Tencent.setIsPermissionGranted(true, Build.MODEL);
        mTencent=Tencent.createInstance("102007045", this,"com.tencent.login.fileprovider");
        DialogX.init(this);
        DialogX.globalStyle = new IOSStyle();
        BaseOkHttp.serviceUrl = settings.getString("http_base_url", getResources().getString(R.string.http_base_url_default));
        user = new User();
        tts = new TTS();
        tts.speek("欢迎使用AiSee，赛题：A3-视障人士友好的资讯辅助软件",false,false);
        tts.speek("准备就绪，请开始使用",false,false);

        registerActivityLifecycleCallbacks(new ActivityLifecycleCallbacks() {
            @Override
            public void onActivityCreated(@NonNull Activity activity, @Nullable Bundle bundle) {

            }

            @Override
            public void onActivityStarted(@NonNull Activity activity) {
                count++;
            }

            @Override
            public void onActivityResumed(@NonNull Activity activity) {

            }

            @Override
            public void onActivityPaused(@NonNull Activity activity) {

            }

            @Override
            public void onActivityStopped(@NonNull Activity activity) {
                count--;
                if (count == 0) {
                    tts.speek("应用切至后台",false,false);
                }
            }

            @Override
            public void onActivitySaveInstanceState(@NonNull Activity activity, @NonNull Bundle bundle) {

            }

            @Override
            public void onActivityDestroyed(@NonNull Activity activity) {

            }
        });


    }


}
