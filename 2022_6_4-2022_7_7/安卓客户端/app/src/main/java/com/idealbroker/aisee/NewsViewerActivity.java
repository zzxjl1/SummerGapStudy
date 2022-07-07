package com.idealbroker.aisee;

import androidx.appcompat.app.AppCompatActivity;
import androidx.webkit.WebViewAssetLoader;
import androidx.webkit.WebViewClientCompat;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.EditText;
import android.widget.TextView;

import com.kongzue.baseokhttp.util.BaseOkHttp;
import com.kongzue.dialogx.dialogs.BottomDialog;
import com.kongzue.dialogx.dialogs.BottomMenu;
import com.kongzue.dialogx.dialogs.PopTip;
import com.kongzue.dialogx.interfaces.DialogLifecycleCallback;
import com.kongzue.dialogx.interfaces.OnBindView;
import com.kongzue.dialogx.style.IOSStyle;
import com.kongzue.dialogx.style.MaterialStyle;

public class NewsViewerActivity extends AppCompatActivity {
    public static WebView webView;
    public static NewsViewerActivity base;
    private int newsId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_news_viewer);
        base = this;

        //获取启动该Activity的Intent对象
        Intent intent = getIntent();
        //获取Intent中暂存的数据
        newsId = intent.getIntExtra("id", -1);
        final WebViewAssetLoader assetLoader = new WebViewAssetLoader.Builder()
                .setDomain("aisee.idealbroker.cn")
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();
        webView = findViewById(R.id.webView);
        ToolUtils.syncCookie(webView);
        webView.setVerticalScrollBarEnabled(false);
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setSupportZoom(false);
        webSettings.setJavaScriptCanOpenWindowsAutomatically(true);
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        webSettings.setDomStorageEnabled(true);
        webSettings.setAppCacheEnabled(true);
        webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        webSettings.setAppCachePath(getApplication().getCacheDir().getAbsolutePath());
        webSettings.setDatabaseEnabled(true);
        webSettings.setUserAgentString(webSettings.getUserAgentString() + " AiSee/" + ToolUtils.getLocalVersion(getApplicationContext()));
        webView.setWebViewClient(new WebViewClientCompat() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return assetLoader.shouldInterceptRequest(request.getUrl());
            }
        });
        webView.addJavascriptInterface(new Object() {
            @JavascriptInterface
            public int getNewsId() {
                return newsId;
            }

            @JavascriptInterface
            public void exit() {
                finish();
            }

            @JavascriptInterface
            public String get_httpBaseUrl() {
                return BaseOkHttp.serviceUrl;
            }

            @JavascriptInterface
            public String get_wsBaseUrl() {
                return MyApplication.settings.getString("ws_base_url", MyApplication.context.getResources().getString(R.string.ws_base_url_default));
            }

            @JavascriptInterface
            public String get_token() {
                return MyApplication.user.getToken();
            }

            @JavascriptInterface
            public void speek(String text, boolean preemptive, boolean flush_queue) {
                MyApplication.tts.speek(text, preemptive, flush_queue);
            }

            @JavascriptInterface
            public void toast(String t) {
                ToolUtils.showToastMessage(NewsViewerActivity.this, t, 2000);
            }

            @JavascriptInterface
            public void reply_to_news() {
                showReplyDialog();
            }

            @JavascriptInterface
            public void showNewsDetail(int id) {
                Intent intent = new Intent(NewsViewerActivity.this, NewsViewerActivity.class);
                intent.putExtra("id", id);
                startActivity(intent);
            }
        }, "JS");
        webView.loadUrl("https://aisee.idealbroker.cn/assets/html/newsviewer.html");
        webView.setWebContentsDebuggingEnabled(true);
        MyApplication.tts.speek("查看新闻详情",true,true);
    }

    @Override
    protected void onDestroy() {
        MyApplication.tts.speek("退出查看", true, true);
        if (webView != null) {
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }

    public void showIME(EditText editText) {
        if (editText == null) {
            return;
        }
        editText.requestFocus();
        editText.setFocusableInTouchMode(true);
        InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
        imm.showSoftInput(editText, InputMethodManager.RESULT_UNCHANGED_SHOWN);
    }

    void send_reply_to_news(String t) {
        NewsViewerActivity.base.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                webView.evaluateJavascript(String.format("cxt.send_reply_to_news(`%s`)", t), new ValueCallback<String>() {
                    @Override
                    public void onReceiveValue(String s) {

                    }
                });
            }
        });
    }

    EditText editReplyCommit;

    void showReplyDialog() {
        BottomDialog.show(new OnBindView<BottomDialog>(R.layout.layout_reply) {

            @Override
            public void onBind(final BottomDialog dialog, View v) {
                View btnReplyCommit = v.findViewById(R.id.btn_reply_commit);
                editReplyCommit = v.findViewById(R.id.edit_reply_commit);
                btnReplyCommit.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        dialog.dismiss();
                        send_reply_to_news(editReplyCommit.getText().toString());
                    }
                });
                editReplyCommit.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        showIME(editReplyCommit);
                    }
                }, 100);
            }
        }).setAllowInterceptTouch(false).setDialogLifecycleCallback(new DialogLifecycleCallback<BottomDialog>() {
            @Override
            public void onDismiss(BottomDialog dialog) {
                super.onDismiss(dialog);
                InputMethodManager manager = (InputMethodManager) getApplicationContext().getSystemService(Context.INPUT_METHOD_SERVICE);
                manager.hideSoftInputFromWindow(editReplyCommit.getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);
            }
        });
    }
}