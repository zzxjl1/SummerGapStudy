<template>
  <div class="frame">
    <br>
    <h2>工具箱</h2>
    <br>
    <br>

    <div class="item" onclick="JS.obj()" style="background: #2195f31c;color: #2196f3;">
      <h3>AI识物</h3>
      <div>对取景框中的物体进行识别并提示用户 </div>
    </div>

    <div class="item" onclick="JS.ocr()" style="background: #ff980014;color: #ff9800;">
      <h3>AI读书</h3>
      <div>通过OCR和TTS辅助阅读</div>
    </div>
    <!--
     <div class="item" style="background: #4caf5014;color: #4caf50;">
      <h3>tts test</h3>
      <div>tts test</div>
    </div>
    -->
  </div>
</template>
<style scoped>
.frame {
  padding-left: 20px;
  padding-right: 20px;
}

h2 {
  padding: 0;
  margin: 0;
  text-align: left;
}

.item {
  cursor: pointer;
  position: relative;
  border-radius: 4px;
  padding: 16px;
  transition: .3s cubic-bezier(.25, .8, .5, 1);
  margin-bottom: 15px;
}

.item>h3 {
  margin: 0;
}
</style>


