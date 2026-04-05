(function () {
    // prevent duplicate splash
    if (document.getElementById("custom-splash")) return;

    const splash = document.createElement("div");

    splash.innerHTML = `
        <div id="custom-splash" style="
            position:fixed;
            top:0;
            left:0;
            width:100%;
            height:100%;
            background:#ffffff;
            display:flex;
            align-items:center;
            justify-content:center;
            z-index:999999;
            flex-direction:column;
            transition: all 0.5s ease;
        ">
            <img src="/assets/pe_erp/images/unnamed.png"
                 style="width:120px;margin-bottom:20px;animation: fadeIn 0.6s ease;" />

            <div style="
                width:0;
                height:4px;
                background:#F15A24;
                animation: loading 1.2s ease-in-out infinite alternate;
            "></div>
        </div>
    `;

    document.body.appendChild(splash);

    // transition white → black
    setTimeout(() => {
        const el = document.getElementById("custom-splash");
        if (el) el.style.background = "#0F0F0F";
    }, 300);

    // remove splash smoothly
    setTimeout(() => {
        splash.style.opacity = "0";
        setTimeout(() => splash.remove(), 500);
    }, 1800);
})();