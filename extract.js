// ==UserScript==
// @name         Extract Geo Problems
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  extract geometry problems from aops imo shortlist
// @author       You
// @match        https://artofproblemsolving.com/community/c3223_imo_shortlist
// @grant        none
// ==/UserScript==

// much rather tap into the api
// need to auto scroll to reveal more problems this way.

function extract() {
    let $ = window.jQuery;
    let dividers = $(".cmty-view-posts-item:not(.cmty-view-post-item-w-label)");
    let out = [];
    dividers.each(function(index, divider) {
        // ignore everything except for geometry dividers
        divider = $(divider);
        if (!/Geometry/i.test(divider.text())) return;
        let title = divider.closest(".cmty-category-cell").find("div.cmty-category-cell-desc").first().text().trim();
        let sibling = divider.next()
        while (sibling[0] !== undefined) {
            let number = sibling.find("div.cmty-view-post-item-label").text();
            let content = sibling.find("div.cmty-view-post-item-text");
            // add alt of image next to it
            content.find("img.latex").each(function(index, element) {
                $(`<span>${$(element).attr("alt")}</span>`).insertAfter(element);
            })
            // yield is not defined
            out.push({
                contest: title,
                number: number,
                content: content.text()
            })
            sibling = sibling.next(".cmty-view-post-item-w-label");
        }
    })
    return out;
}

window.extract = extract
