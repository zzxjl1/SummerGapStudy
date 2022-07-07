package com.idealbroker.aisee;

import static com.idealbroker.aisee.ToolUtils.dp2px;

import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.TextView;

import androidx.webkit.WebViewAssetLoader;
import androidx.webkit.WebViewClientCompat;

import com.hjq.permissions.OnPermissionCallback;
import com.hjq.permissions.Permission;
import com.hjq.permissions.XXPermissions;
import com.idealbroker.aisee.opencv.Camera2View;
import com.kongzue.baseokhttp.HttpRequest;
import com.kongzue.baseokhttp.listener.ResponseListener;
import com.kongzue.baseokhttp.util.BaseOkHttp;
import com.kongzue.baseokhttp.util.Parameter;
import com.kongzue.dialogx.dialogs.FullScreenDialog;
import com.kongzue.dialogx.dialogs.WaitDialog;
import com.kongzue.dialogx.interfaces.DialogLifecycleCallback;
import com.kongzue.dialogx.interfaces.OnBindView;
import com.kongzue.dialogx.util.views.ActivityScreenShotImageView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.opencv.core.Mat;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;


public class OCRActivity extends CameraActivity {
    private String TAG = "AIRead";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        toggle_assist_mode(true);
        super.onCreate(savedInstanceState);
        MyApplication.tts.speek("AI读书", false, false);
        MyApplication.tts.speek("请将要识别的页面放置在红色方框区域内，并按下拍照按钮", false, false);

        if (!XXPermissions.isGranted(this, Permission.CAMERA)) {
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
        MyApplication.tts.speek("退出AI读书", true, true);
    }


    @Override
    public void onCapture(Bitmap bmp) {
        bmp = Bitmap.createBitmap(bmp,crop_rect.x,crop_rect.y,crop_rect.width,crop_rect.height);
        File PATH = new File(getCacheDir(), "ocr");
        if (!PATH.exists()) PATH.mkdir();
        File file = new File(PATH, "ocr_temp.jpg");
        try (FileOutputStream out = new FileOutputStream(file)) {
            bmp.compress(Bitmap.CompressFormat.JPEG, 80, out);
            WaitDialog.show("请求中");
            HttpRequest.POST(this, "/ocr", new Parameter().add("file", file), new ResponseListener() {
                @Override
                public void onResponse(String response, Exception error) {
                    WaitDialog.dismiss();
                    MyApplication.tts.speek("云端处理中，请稍后", true, true);
                    if (error != null) {
                        ToolUtils.showToastMessage(OCRActivity.this, "网络请求失败", 2000);
                        return;
                    }

                    try {
                        Log.e(TAG, response);
                        JSONObject t = new JSONObject(response);
                        if (t.getBoolean("success")) {
                            String content = t.getString("content");
                            if (content.isEmpty()) {
                                ToolUtils.showToastMessage(OCRActivity.this, "没有识别到内容", 2000);
                                return;
                            }
                            showFullscreenDialog(content);

                        } else {
                            ToolUtils.showToastMessage(OCRActivity.this, t.getString("message"), 2000);
                        }
                    } catch (JSONException e) {
                        ToolUtils.showToastMessage(OCRActivity.this, e.getMessage(), 2000);
                    }


                }
            });


        } catch (
                IOException e) {
            e.printStackTrace();
        }
    }
    Rect crop_rect = null;
    @Override
    public Mat onCameraFrame(Camera2View.Camera2Frame inputFrame) {

        Mat t = super.onCameraFrame(inputFrame);
        if(crop_rect==null){
            int w = t.width();
            int h = t.height();
            int margin_left_right = dp2px(OCRActivity.this,60);
            int margin_top = dp2px(OCRActivity.this,110);
            int margin_bottom  =dp2px(OCRActivity.this,160);
            crop_rect = new Rect(margin_top, margin_left_right,w-margin_bottom-margin_top , h-margin_left_right*2);
        }

        Imgproc.rectangle(t, new Point(crop_rect.x,crop_rect.y), new Point(
                crop_rect.width+crop_rect.x , crop_rect.height+crop_rect.y), new Scalar(255, 0, 0), 20);

        return t;
    }
    WebView webView;
    private void showFullscreenDialog(String t) {
        FullScreenDialog.build(new OnBindView<FullScreenDialog>(R.layout.layout_full_webview) {
            @Override
            public void onBind(final FullScreenDialog dialog, View v) {
                View btnClose = v.findViewById(R.id.btn_close);
                webView = v.findViewById(R.id.webView);
                webView.addJavascriptInterface(new Object() {
                    @JavascriptInterface
                    public String fetch() {
                        return t;
                    }
                    @JavascriptInterface
                    public String get_httpBaseUrl() {
                        return BaseOkHttp.serviceUrl;
                    }
                }, "JS");
                btnClose.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        dialog.dismiss();
                    }
                });

                WebSettings webSettings = webView.getSettings();
                webSettings.setJavaScriptEnabled(true);
                webSettings.setLoadWithOverviewMode(true);
                webSettings.setUseWideViewPort(true);
                webSettings.setSupportZoom(false);
                webSettings.setJavaScriptCanOpenWindowsAutomatically(true);
                webSettings.setLoadsImagesAutomatically(true);
                webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
                webSettings.setMediaPlaybackRequiresUserGesture(false);
                final WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
                        .setDomain("aisee.idealbroker.cn")
                        .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(OCRActivity.this))
                        .build();
                webView.setWebViewClient(new WebViewClientCompat() {
                    @Override
                    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                        return assetLoader.shouldInterceptRequest(request.getUrl());
                    }
                });
                webView.loadUrl("https://aisee.idealbroker.cn/assets/html/ocr.html");
                webView.setWebContentsDebuggingEnabled(true);

            }
        }).setHideZoomBackground(true).setDialogLifecycleCallback(new DialogLifecycleCallback<FullScreenDialog>() {
            @Override
            public void onDismiss(FullScreenDialog dialog) {
                super.onDismiss(dialog);
                webView.destroy();
            }
        }).show();
    }

}