package com.crownfall.stronghold;

import android.app.Activity;
import android.content.pm.ApplicationInfo;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView webView;

    private void immersive() {
        View decor = getWindow().getDecorView();
        if (decor == null) return;

        if (android.os.Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController controller = decor.getWindowInsetsController();
            if (controller != null) {
                controller.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                controller.setSystemBarsBehavior(
                    WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                );
            }
        } else {
            decor.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            );
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        webView.setBackgroundColor(0xFF061017);
        setContentView(webView);
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                if ((getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
                    view.evaluateJavascript(
                        "document.getElementById('start') ? 'START_OK' : 'START_MISSING'",
                        value -> Log.i("CROWNFALL_SMOKE", "DOM=" + value)
                    );

                    String gameplaySmoke = """
                        (function(){
                          window.__CROWNFALL_GAMEPLAY_SMOKE='RUNNING';
                          const fail=(m)=>{window.__CROWNFALL_GAMEPLAY_SMOKE='FAIL:'+m;};
                          try{
                            const splash=document.getElementById('splash');
                            if(!splash) return fail('splash-missing');
                            s.soundOn=false;
                            splash.style.display='none';
                            ensureDaily();
                            render();
                            setTimeout(()=>{
                              try{
                                const beforeBuildings=s.b.length, beforeGuards=s.guards;
                                const buildBtn=document.getElementById('buildBtn');
                                if(!buildBtn) return fail('build-button-missing');
                                buildBtn.click();
                                const card=[...document.querySelectorAll('#drawer .card')].find(x=>!x.disabled);
                                if(!card) return fail('build-card-missing');
                                card.click();

                                const mapEl=document.getElementById('map');
                                const r=mapEl.getBoundingClientRect();
                                let pt=null;
                                outer: for(let y=22;y<=76;y+=4){
                                  for(let x=12;x<=88;x+=4){
                                    const crowded=s.b.some(o=>Math.hypot((o.x-x)*1.25,o.y-y)<8);
                                    if(!crowded){pt={x,y};break outer;}
                                  }
                                }
                                if(!pt) return fail('no-build-space');

                                mapEl.dispatchEvent(new MouseEvent('click',{
                                  bubbles:true,
                                  clientX:r.left+r.width*pt.x/100,
                                  clientY:r.top+r.height*pt.y/100
                                }));

                                setTimeout(()=>{
                                  try{
                                    if(!s.pendingBuild) return fail('preview-not-opened');
                                    const confirm=document.getElementById('ovAction');
                                    if(!confirm) return fail('confirm-missing');
                                    confirm.click();

                                    setTimeout(()=>{
                                      try{
                                        if(s.b.length!==beforeBuildings+1) return fail('build-not-added');
                                        document.getElementById('trainBtn').click();
                                        if(s.guards!==beforeGuards+1) return fail('guard-not-trained');

                                        document.getElementById('battleBtn').click();
                                        if(!battleState || !document.getElementById('combatArena')) return fail('battle-not-started');

                                        const turnBefore=battleState.turn;
                                        document.getElementById('ovAction').click();

                                        setTimeout(()=>{
                                          try{
                                            const combatAdvanced=(battleState && battleState.turn>turnBefore) || (!battleState && s.battles>0);
                                            if(!combatAdvanced) return fail('combat-turn-not-advanced');
                                            window.__CROWNFALL_GAMEPLAY_SMOKE=
                                              'PASS:buildings='+s.b.length+',guards='+s.guards+',battles='+s.battles+',tutorial='+s.tutorialStep;
                                          }catch(e){fail('combat-check:'+e.message);}
                                        },300);
                                      }catch(e){fail('battle-step:'+e.message);}
                                    },350);
                                  }catch(e){fail('build-confirm:'+e.message);}
                                },250);
                              }catch(e){fail('build-step:'+e.message);}
                            },900);
                          }catch(e){fail('start-step:'+e.message);}
                        })();
                        """;

                    view.evaluateJavascript(gameplaySmoke, null);
                    view.postDelayed(() -> view.evaluateJavascript(
                        "window.__CROWNFALL_GAMEPLAY_SMOKE || 'PENDING'",
                        value -> Log.i("CROWNFALL_GAMEPLAY_SMOKE", "RESULT=" + value)
                    ), 5000);
                }
            }
        });
        webView.setWebChromeClient(new WebChromeClient());

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setLoadsImagesAutomatically(true);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setSupportZoom(false);

        webView.loadUrl("file:///android_asset/www/index.html");
        webView.post(this::immersive);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) {
            webView.onResume();
            webView.post(this::immersive);
        }
    }

    @Override
    protected void onPause() {
        if (webView != null) webView.onPause();
        super.onPause();
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }
}
