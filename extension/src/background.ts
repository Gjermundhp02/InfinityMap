function listener(reqID: string) {
    let filter = browser.webRequest.filterResponseData(reqID);
    let decoder = new TextDecoder("utf-8");
    let json = "";

    filter.ondata = event => {
        let str = decoder.decode(event.data, {stream: true});
        json += str;
        filter.write(event.data);
    }

    filter.onstop = event => {
        (async () => {
            const [tab] = await browser.tabs.query({active: true, currentWindow: true});
            const response = await browser.tabs.sendMessage(tab.id, JSON.parse(json));
            console.log(response);
            filter.close();
        })();
    }
}

browser.webRequest.onBeforeRequest.addListener((details) => {
    listener(details.requestId);
}, {urls: ["*://neal.fun/api/infinite-craft/pair*"]}, ["blocking"]);

console.log("Background script loaded");