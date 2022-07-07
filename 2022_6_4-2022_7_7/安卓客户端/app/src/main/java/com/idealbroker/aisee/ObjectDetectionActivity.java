package com.idealbroker.aisee;

import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import com.hjq.permissions.OnPermissionCallback;
import com.hjq.permissions.Permission;
import com.hjq.permissions.XXPermissions;
import com.kongzue.baseokhttp.HttpRequest;
import com.kongzue.baseokhttp.listener.ResponseListener;
import com.kongzue.baseokhttp.util.Parameter;
import com.kongzue.dialogx.dialogs.FullScreenDialog;
import com.kongzue.dialogx.dialogs.WaitDialog;
import com.kongzue.dialogx.interfaces.OnBindView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;


public class ObjectDetectionActivity extends CameraActivity {
    private String TAG = "AIRec";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        toggle_assist_mode(true);
        super.onCreate(savedInstanceState);
        MyApplication.tts.speek("AI识物", false, false);
        MyApplication.tts.speek("请将镜头对准要识别的页面，并拍照", false, false);

        if(!XXPermissions.isGranted(this,Permission.CAMERA)){
            MyApplication.tts.speek("本功能需要相机权限，请在弹出的对话框中点击“允许”按钮！", true, true);
            XXPermissions.with(this)
                    .permission(Permission.CAMERA)
                    .request(new OnPermissionCallback() {

                        @Override
                        public void onGranted(List<String> permissions, boolean all) {

                        }

                        @Override
                        public void onDenied(List<String> permissions, boolean never) {
                            ToolUtils.showToastMessage(MyApplication.context, "权限获取失败", 2000);
                            MyApplication.tts.speek("权限获取失败，功能退出！", true, true);
                            finish();
                        }
                    });
        }

    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        MyApplication.tts.speek("退出AI识物", true, true);
    }

    void speek(String t) {
        MyApplication.tts.speek("识别结果为：" + t, true, true);
    }

    @Override
    public void onCapture(Bitmap bmp) {
        File PATH = new File(getCacheDir(), "obj");
        if (!PATH.exists()) PATH.mkdir();
        File file = new File(PATH, "obj_temp.jpg");
        try (FileOutputStream out = new FileOutputStream(file)) {
            bmp.compress(Bitmap.CompressFormat.JPEG, 80, out);
            WaitDialog.show("请求中");
            HttpRequest.POST(this, "/obj", new Parameter().add("file", file), new ResponseListener() {
                @Override
                public void onResponse(String response, Exception error) {
                    WaitDialog.dismiss();
                    MyApplication.tts.speek("云端处理中，请稍后", true, true);
                    if (error != null) {
                        ToolUtils.showToastMessage(ObjectDetectionActivity.this, "网络请求失败", 2000);
                        return;
                    }

                    try {
                        Log.e(TAG, response);
                        JSONObject t = new JSONObject(response);
                        if (t.getBoolean("success")) {
                            JSONArray result = t.getJSONArray("content");
                            String content = "";
                            for (int i = 0; i < result.length(); i++) {
                                content += "· " + result.getString(i) + "\n";
                            }
                            speek(content);
                            String finalContent = content;
                            FullScreenDialog.build(new OnBindView<FullScreenDialog>(R.layout.objdetect_view) {
                                @Override
                                public void onBind(FullScreenDialog dialog, View rootView) {
                                    View btnClose = rootView.findViewById(R.id.btn_cancel);
                                    TextView textView = rootView.findViewById(R.id.result_list);
                                    View speekButton = rootView.findViewById(R.id.speek_button);
                                    textView.setText(finalContent.toCharArray(), 0, finalContent.length());
                                    speekButton.setOnClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View view) {
                                            speek(finalContent);
                                        }
                                    });
                                    btnClose.setOnClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            dialog.dismiss();
                                        }
                                    });
                                }
                            }).setHideZoomBackground(true).show();

                        } else {
                            ToolUtils.showToastMessage(ObjectDetectionActivity.this, t.getString("message"), 2000);
                        }
                    } catch (JSONException e) {
                        ToolUtils.showToastMessage(ObjectDetectionActivity.this, e.getMessage(), 2000);
                    }


                }
            });


        } catch (
                IOException e) {
            e.printStackTrace();
        }
    }

}