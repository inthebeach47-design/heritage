
    (function() {
      var preconnectOrigins = ["https://cdn.shopify.com"];
      var scripts = ["/cdn/shopifycloud/checkout-web/assets/c1/polyfills.Cm4XMvKf.js","/cdn/shopifycloud/checkout-web/assets/c1/app.cAthPeiN.js","/cdn/shopifycloud/checkout-web/assets/c1/2c1ab0fe.DrRCn3HG.js","/cdn/shopifycloud/checkout-web/assets/c1/6a2fc6d6.DqfKWMZb.js","/cdn/shopifycloud/checkout-web/assets/c1/5587f402.BLOv5NpY.js","/cdn/shopifycloud/checkout-web/assets/c1/cf29e63b.BRQXh2EH.js","/cdn/shopifycloud/checkout-web/assets/c1/bfe75f31.6yCNtNv-.js","/cdn/shopifycloud/checkout-web/assets/c1/8b3289d0.Bt3qZnT_.js","/cdn/shopifycloud/checkout-web/assets/c1/2255f8fa.DOeij2sJ.js","/cdn/shopifycloud/checkout-web/assets/c1/204243fa.V7gQ36sj.js","/cdn/shopifycloud/checkout-web/assets/c1/5c5817f3.BEu0evcd.js","/cdn/shopifycloud/checkout-web/assets/c1/8f46f026.Bz0NEFVt.js","/cdn/shopifycloud/checkout-web/assets/c1/f05935e5.bhemP6c2.js","/cdn/shopifycloud/checkout-web/assets/c1/32e8c018.BVeb327i.js","/cdn/shopifycloud/checkout-web/assets/c1/7336bdaf.DcxaUsDT.js","/cdn/shopifycloud/checkout-web/assets/c1/6f2620f5.D_02a169.js","/cdn/shopifycloud/checkout-web/assets/c1/cf6ddc11.DMeQLHv7.js","/cdn/shopifycloud/checkout-web/assets/c1/b8733b27.C0PFpUAK.js","/cdn/shopifycloud/checkout-web/assets/c1/e39bc11c.BaBGTrLm.js","/cdn/shopifycloud/checkout-web/assets/c1/08a3b809.DQs60AXV.js","/cdn/shopifycloud/checkout-web/assets/c1/164ad2e3.B1TfVO1E.js","/cdn/shopifycloud/checkout-web/assets/c1/69fae6d4.B0cVlpvy.js","/cdn/shopifycloud/checkout-web/assets/c1/e12db40c.BI5RQVDa.js","/cdn/shopifycloud/checkout-web/assets/c1/60a453ce.DXa3DaPc.js","/cdn/shopifycloud/checkout-web/assets/c1/fb3b4968.B33l1A_z.js","/cdn/shopifycloud/checkout-web/assets/c1/f8706cb6.DmSw67Cj.js","/cdn/shopifycloud/checkout-web/assets/c1/0e9ee714.wULXKuPc.js","/cdn/shopifycloud/checkout-web/assets/c1/39921a74.3CxTFnjT.js","/cdn/shopifycloud/checkout-web/assets/c1/7a8217fd.BBDsaE4D.js","/cdn/shopifycloud/checkout-web/assets/c1/8599b02a.SMqdFzKQ.js","/cdn/shopifycloud/checkout-web/assets/c1/dffdfb34.CMQnj3Km.js","/cdn/shopifycloud/checkout-web/assets/c1/a422df8c.DOeqFAvq.js","/cdn/shopifycloud/checkout-web/assets/c1/efa0389a.DrLHo2nc.js","/cdn/shopifycloud/checkout-web/assets/c1/c8760fd8.Be0EZ9hi.js","/cdn/shopifycloud/checkout-web/assets/c1/53bbdad9.CVg-OYc7.js","/cdn/shopifycloud/checkout-web/assets/c1/1f5e7811.DFPNjnst.js","/cdn/shopifycloud/checkout-web/assets/c1/1a6c2867.DIvU9A1-.js","/cdn/shopifycloud/checkout-web/assets/c1/2fdb3dd3.CTDVcfb6.js","/cdn/shopifycloud/checkout-web/assets/c1/22345fd4.BAghc-fu.js","/cdn/shopifycloud/checkout-web/assets/c1/0e67bd3b.CFeNdDM-.js","/cdn/shopifycloud/checkout-web/assets/c1/a9fa9fda.BeDDbBvp.js","/cdn/shopifycloud/checkout-web/assets/c1/ca3e798e.Dl0SRkiU.js","/cdn/shopifycloud/checkout-web/assets/c1/f7861534.Bd8yhhUE.js","/cdn/shopifycloud/checkout-web/assets/c1/47b970b2.BXt-43WV.js","/cdn/shopifycloud/checkout-web/assets/c1/064f6ac1.4EMhYNtA.js","/cdn/shopifycloud/checkout-web/assets/c1/17425706.BcJPt7Oh.js","/cdn/shopifycloud/checkout-web/assets/c1/71ae3d5c.DH-HAOXQ.js","/cdn/shopifycloud/checkout-web/assets/c1/cb5cf153.r_2iWLRe.js","/cdn/shopifycloud/checkout-web/assets/c1/06ef5503.Dv-zBuK4.js","/cdn/shopifycloud/checkout-web/assets/c1/acc42fa8.DaJQita_.js","/cdn/shopifycloud/checkout-web/assets/c1/cccd6056.DePXU1Wc.js","/cdn/shopifycloud/checkout-web/assets/c1/0b8657b8.D-I2um0-.js","/cdn/shopifycloud/checkout-web/assets/c1/79974aab.zZ2KWkIs.js","/cdn/shopifycloud/checkout-web/assets/c1/89e2d30a.BYEQZ8wJ.js","/cdn/shopifycloud/checkout-web/assets/c1/ed9f2238.hwBClo-8.js","/cdn/shopifycloud/checkout-web/assets/c1/6fb6f9d8.BAMqjCt6.js","/cdn/shopifycloud/checkout-web/assets/c1/1444e6bd.BM7R-elq.js","/cdn/shopifycloud/checkout-web/assets/c1/55098bf1.Dz8MQz2P.js","/cdn/shopifycloud/checkout-web/assets/c1/f49d4216.CDFLXjau.js","/cdn/shopifycloud/checkout-web/assets/c1/7b0c98ea.CRpHa0fS.js","/cdn/shopifycloud/checkout-web/assets/c1/d22d2b80.jfu5yGpw.js","/cdn/shopifycloud/checkout-web/assets/c1/f58f39d8.wWS96b1U.js","/cdn/shopifycloud/checkout-web/assets/c1/e03065ab.CWf9aWZN.js","/cdn/shopifycloud/checkout-web/assets/c1/c09515bf.B71fejgK.js","/cdn/shopifycloud/checkout-web/assets/c1/6bfea526.B0c9qjLX.js","/cdn/shopifycloud/checkout-web/assets/c1/ac5a19ff.ns171nJ5.js","/cdn/shopifycloud/checkout-web/assets/c1/598fef4e.DygUyRW2.js","/cdn/shopifycloud/checkout-web/assets/c1/e77f7fe0.DFN8f_R0.js","/cdn/shopifycloud/checkout-web/assets/c1/cc6ff67d.DVXb3TBr.js","/cdn/shopifycloud/checkout-web/assets/c1/bf513f9c.Do-pzA-t.js","/cdn/shopifycloud/checkout-web/assets/c1/dfca5da5.Aek1wZmx.js","/cdn/shopifycloud/checkout-web/assets/c1/dae24aab.Ddqlep8a.js","/cdn/shopifycloud/checkout-web/assets/c1/ddf59287.CYD1TGGD.js","/cdn/shopifycloud/checkout-web/assets/c1/01973ac7.DH2lZj47.js","/cdn/shopifycloud/checkout-web/assets/c1/58314944.C8tOb_bS.js","/cdn/shopifycloud/checkout-web/assets/c1/945a08d6.1JARX8O_.js","/cdn/shopifycloud/checkout-web/assets/c1/a25deb9a.DxN44MdX.js","/cdn/shopifycloud/checkout-web/assets/c1/2b89a178.CjdbXfg7.js","/cdn/shopifycloud/checkout-web/assets/c1/9068a4ed.D9qjdpv1.js","/cdn/shopifycloud/checkout-web/assets/c1/b684bff6.8wYVCzKV.js","/cdn/shopifycloud/checkout-web/assets/c1/f1968089.yy6CXKcX.js","/cdn/shopifycloud/checkout-web/assets/c1/910cd6e2.DS6ygtkl.js","/cdn/shopifycloud/checkout-web/assets/c1/347b440c.DPGZDqyz.js","/cdn/shopifycloud/checkout-web/assets/c1/5ade1ef3.DXB4L25S.js","/cdn/shopifycloud/checkout-web/assets/c1/181d38d3.C2MFP83j.js","/cdn/shopifycloud/checkout-web/assets/c1/5a347040.DqqqLoQW.js","/cdn/shopifycloud/checkout-web/assets/c1/792bb671.MG_raAxs.js","/cdn/shopifycloud/checkout-web/assets/c1/9ca7d819.B_r4aISK.js","/cdn/shopifycloud/checkout-web/assets/c1/f51e663e.D1Mwbrt6.js","/cdn/shopifycloud/checkout-web/assets/c1/21cc90a2.DHzOO82q.js","/cdn/shopifycloud/checkout-web/assets/c1/64de7b49.B2WWgZOD.js","/cdn/shopifycloud/checkout-web/assets/c1/ca0c3e72.mAtaVirp.js","/cdn/shopifycloud/checkout-web/assets/c1/8e79be58.C8MS0jza.js","/cdn/shopifycloud/checkout-web/assets/c1/90e26f5f.Dtj-XP1M.js","/cdn/shopifycloud/checkout-web/assets/c1/31cc568e.95lmLO5k.js","/cdn/shopifycloud/checkout-web/assets/c1/65f3d4da.Bb3QiqCm.js","/cdn/shopifycloud/checkout-web/assets/c1/d5d34b3b.BdlOFFHa.js","/cdn/shopifycloud/checkout-web/assets/c1/ca5e9c49.DTB5eJ2J.js","/cdn/shopifycloud/checkout-web/assets/c1/f3e117aa.DTJ0PR2t.js","/cdn/shopifycloud/checkout-web/assets/c1/7aefefff.DcUdfhSw.js","/cdn/shopifycloud/checkout-web/assets/c1/b3389d5c.fiS1Nr-I.js","/cdn/shopifycloud/checkout-web/assets/c1/73a9b0a0.BRydut8V.js","/cdn/shopifycloud/checkout-web/assets/c1/86720dbb.B5HdvqVg.js","/cdn/shopifycloud/checkout-web/assets/c1/0724c71d.O32rwBsR.js","/cdn/shopifycloud/checkout-web/assets/c1/7114e006.lrS99emJ.js","/cdn/shopifycloud/checkout-web/assets/c1/9babe369.ocvpn2KV.js","/cdn/shopifycloud/checkout-web/assets/c1/434e3b0a.oup8Ur0H.js","/cdn/shopifycloud/checkout-web/assets/c1/e0989459.BN6EGpPC.js","/cdn/shopifycloud/checkout-web/assets/c1/cdfd59e6.Cs835jgd.js","/cdn/shopifycloud/checkout-web/assets/c1/d2e6a587.Bvz9lXAd.js","/cdn/shopifycloud/checkout-web/assets/c1/ca3c8263.DkbnVCmF.js","/cdn/shopifycloud/checkout-web/assets/c1/083cdde5.DYEjGEf-.js","/cdn/shopifycloud/checkout-web/assets/c1/fe885b80.rUOq8lM6.js","/cdn/shopifycloud/checkout-web/assets/c1/f78726c8.ClHl3T7C.js","/cdn/shopifycloud/checkout-web/assets/c1/d93ca466.C9R5umgP.js","/cdn/shopifycloud/checkout-web/assets/c1/e129c76e.SSgFk5gO.js","/cdn/shopifycloud/checkout-web/assets/c1/051149c8.lHD9iIAq.js","/cdn/shopifycloud/checkout-web/assets/c1/d7065744.CK6x5CHa.js","/cdn/shopifycloud/checkout-web/assets/c1/7ee73f43.ZeHo6koi.js","/cdn/shopifycloud/checkout-web/assets/c1/0c0ad074.BLLdTe6K.js","/cdn/shopifycloud/checkout-web/assets/c1/8fe56fc9.DKeGEDf5.js","/cdn/shopifycloud/checkout-web/assets/c1/2210eadb.DF0gIp_2.js","/cdn/shopifycloud/checkout-web/assets/c1/8a00b682.BEOU-kK4.js","/cdn/shopifycloud/checkout-web/assets/c1/87bfafec.BIoL9TQ3.js","/cdn/shopifycloud/checkout-web/assets/c1/e477f96c.B7RRII2U.js","/cdn/shopifycloud/checkout-web/assets/c1/c6b02d73.DFxNKn7U.js","/cdn/shopifycloud/checkout-web/assets/c1/71b60e0a.Bdvld-6t.js","/cdn/shopifycloud/checkout-web/assets/c1/24773686.C8B24loc.js","/cdn/shopifycloud/checkout-web/assets/c1/7048f38b.Ct0cMld6.js","/cdn/shopifycloud/checkout-web/assets/c1/c3c7c048.B_bxvive.js","/cdn/shopifycloud/checkout-web/assets/c1/7aa3b627.DU4dK-Iv.js","/cdn/shopifycloud/checkout-web/assets/c1/dada7e07.CS-vFszt.js","/cdn/shopifycloud/checkout-web/assets/c1/c10167e6.B31SY0iW.js","/cdn/shopifycloud/checkout-web/assets/c1/17e57de1.DrMLKbeq.js"];
      var styles = ["/cdn/shopifycloud/checkout-web/assets/c1/assets/app.DBH01810.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/is-address-empty.DDArxpAV.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/hydrate.LpOe7KaD.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/OnePage.C_uC3EPz.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/StickyPayButton.D-gNjNDa.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/Switch.BS8yVgoP.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/useShopPayProgressIntercepts.CIy8uDiZ.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/VatNumberValidationField.DZtuG_UK.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/EmptyState.BEvzDDvy.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/Choice.BMdzfW_y.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/ShopPayLogo.87JMHPUK.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/ChangeCompanyLocationLink.B1YSPUDc.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/PhoneField.uZEuHncj.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/Popover.Bi1nHaU-.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/index.Du9dByaI.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/useApplePayButtonStatus.ct4xfivv.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/TransitionHeight.CuRoM9zv.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/Tipping.BcTJoNaV.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/PaymentIcon.gzvCNwz_.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/PaymentLine.DT05kVlY.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/Section.CU18S7Ap.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/findSelectedDeliveryMethod.xO_7ctnq.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/Middot.D7Ujmshx.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/EstimatedDeliveryContent.BAjucZ-8.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/BrandedPromise.B0RErzdh.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/ShippingMethods.DU0m5rdF.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/ShippingMethodSelector.B0hio2RO.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/SubscriptionPriceBreakdown.vTcdVGq4.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/BelowTheFoldContent.DRJckcGa.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/RememberMeSection.JBO5WNhc.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/PaymentMethodProgressionHost.kQR0txJ7.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/RedirectionNotice.B8v_QGNW.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/MissingFields.BbxB_6wt.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/MobileOrderSummary.CyQZvZOO.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/useOnePageFormSubmit.1WzRSowg.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/checkout-pay-button-exit.KhTiKgPS.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/observe-fit-scale.DpLOWYa8.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/useShopPayButtonClassName.btyKOfco.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/Payment.DrWvAMMF.css","/cdn/shopifycloud/checkout-web/assets/c1/assets/PaymentOptionSelector.s-Kd_X2E.css"];
      var fontPreconnectUrls = [];
      var fontPrefetchUrls = [];
      var imgPrefetchUrls = [];

      function preconnect(url, callback) {
        var link = document.createElement('link');
        link.rel = 'dns-prefetch preconnect';
        link.href = url;
        link.crossOrigin = '';
        link.onload = link.onerror = callback;
        document.head.appendChild(link);
      }

      function preconnectAssets() {
        var resources = preconnectOrigins.concat(fontPreconnectUrls);
        var index = 0;
        (function next() {
          var res = resources[index++];
          if (res) preconnect(res, next);
        })();
      }

      function prefetch(url, as, callback) {
        var link = document.createElement('link');
        if (link.relList.supports('prefetch')) {
          link.rel = 'prefetch';
          link.fetchPriority = 'low';
          link.as = as;
          if (as === 'font') link.type = 'font/woff2';
          link.href = url;
          link.crossOrigin = '';
          link.onload = link.onerror = callback;
          document.head.appendChild(link);
        } else {
          var xhr = new XMLHttpRequest();
          xhr.open('GET', url, true);
          xhr.onloadend = callback;
          xhr.send();
        }
      }

      function prefetchAssets() {
        var resources = [].concat(
          scripts.map(function(url) { return [url, 'script']; }),
          styles.map(function(url) { return [url, 'style']; }),
          fontPrefetchUrls.map(function(url) { return [url, 'font']; }),
          imgPrefetchUrls.map(function(url) { return [url, 'image']; })
        );
        var index = 0;
        function run() {
          var res = resources[index++];
          if (res) prefetch(res[0], res[1], next);
        }
        var next = (self.requestIdleCallback || setTimeout).bind(self, run);
        next();
      }

      function onLoaded() {
        try {
          if (parseFloat(navigator.connection.effectiveType) > 2 && !navigator.connection.saveData) {
            preconnectAssets();
            prefetchAssets();
          }
        } catch (e) {}
      }

      if (document.readyState === 'complete') {
        onLoaded();
      } else {
        addEventListener('load', onLoaded);
      }
    })();
  