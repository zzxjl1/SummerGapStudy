package com.idealbroker.aisee;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

import com.kongzue.baseokhttp.HttpRequest;
import com.kongzue.baseokhttp.listener.ResponseListener;
import com.kongzue.baseokhttp.util.Parameter;

import org.json.JSONException;
import org.json.JSONObject;


class User {
    boolean loggedin = false;
    String nickname = "";
    String id = "";
    public SharedPreferences sharedPreferences = PreferenceManager.getDefaultSharedPreferences(MyApplication.context);

    {
        login();
    }

    public boolean is_loggedin() {
        return loggedin;
    }

    public JSONObject getLoginState() {

        JSONObject t = new JSONObject();
        try {
            t.put("logedin", loggedin);
            t.put("nickname", nickname);
            t.put("id", id);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return t;
    }

    public String getToken() {
        return sharedPreferences.getString("token", "");
    }



    public void logout() {
        loggedin = false;
        nickname = "";
        id = "";
        set("token", "");
        if (MainActivity.base != null) {
            MainActivity.refreshLoginState();
        }
    }

    public void login() {
        if (getToken().isEmpty()) return;
        HttpRequest.GET(MyApplication.context, "/user/details",
                new Parameter().add("token", getToken()), new ResponseListener() {
                    @Override
                    public void onResponse(String response, Exception error) {
                        try {
                            if (error != null) return;
                            JSONObject jsonObject = new JSONObject(response);
                            if (jsonObject.getBoolean("success")) {
                                loggedin = true;
                                nickname = jsonObject.getString("nickname");
                                id = jsonObject.getString("id");
                                if (MainActivity.base != null) {
                                    MainActivity.refreshLoginState();
                                }
                            } else {
                                logout();
                            }
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }

                    }
                });

    }

    public void set(String key, String value) {
        sharedPreferences.edit().putString(key, value).apply();
    }
}