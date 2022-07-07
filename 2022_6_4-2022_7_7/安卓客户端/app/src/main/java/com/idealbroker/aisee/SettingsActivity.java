package com.idealbroker.aisee;


import static com.idealbroker.aisee.MyApplication.settings;

import android.content.SharedPreferences;
import android.os.Bundle;

import androidx.appcompat.app.ActionBar;
import androidx.appcompat.app.AppCompatActivity;
import androidx.preference.Preference;
import androidx.preference.PreferenceFragmentCompat;

import com.kongzue.baseokhttp.util.BaseOkHttp;

import java.util.Objects;

public class SettingsActivity extends AppCompatActivity {
    private static SettingsActivity context;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        context=this;
        setContentView(R.layout.settings_activity);
        getSupportFragmentManager()
                .beginTransaction()
                .replace(R.id.settings, new SettingsFragment())
                .commit();
        ActionBar actionBar = getSupportActionBar();
        if (actionBar != null) {
            actionBar.setDisplayHomeAsUpEnabled(true);
        }

    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        MyApplication.tts.speek("退出设置",true,true);

    }
    public static class SettingsFragment extends PreferenceFragmentCompat {
        @Override
        public void onCreatePreferences(Bundle savedInstanceState, String rootKey) {
            setPreferencesFromResource(R.xml.root_preferences, rootKey);
            findPreference("pref_app_version").setSummary(BuildConfig.VERSION_NAME);
            findPreference("pref_system_release").setSummary(android.os.Build.VERSION.RELEASE);
            findPreference("pref_device_model").setSummary(android.os.Build.MODEL);
            findPreference("pref_device_brand").setSummary(android.os.Build.BRAND);

            findPreference("http_base_url").setOnPreferenceChangeListener(new Preference.OnPreferenceChangeListener() {
                @Override
                public boolean onPreferenceChange(Preference preference, Object o) {
                    BaseOkHttp.serviceUrl = o.toString();
                    return true;
                }
            });

            Preference button = findPreference("back_to_default_btn");
            Objects.requireNonNull(button).setOnPreferenceClickListener(new Preference.OnPreferenceClickListener() {
                @Override
                public boolean onPreferenceClick(Preference preference) {
                    SharedPreferences.Editor editor = settings.edit();
                    editor.putString("http_base_url", getResources().getString(R.string.http_base_url_default));
                    editor.putString("ws_base_url", getResources().getString(R.string.ws_base_url_default));
                    editor.apply();

                    context.finish();
                    startActivity(context.getIntent());
                    return true;
                }
            });
            MyApplication.tts.speek("设置",true,true);
        }
    }
}