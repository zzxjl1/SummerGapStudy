package com.idealbroker.aisee;

import com.kongzue.dialogx.dialogs.PopTip;

public class STTCallback {
    String getShortenedString(String text) {
        return text.length() < 10 ? text : text.substring(text.length() - 10);
    }

    void onProcedure(String text) {
        String t = getShortenedString(text);
        PopTip.show(R.mipmap.ai_apeech, t)
                .setAutoTintIconInLightOrDarkMode(false);
    }

    void onEnd(String text) {
        String t = getShortenedString(text);
        PopTip.cleanAll();
        PopTip.show(R.mipmap.ai_apeech, t)
                .setAutoTintIconInLightOrDarkMode(false);
    }

}