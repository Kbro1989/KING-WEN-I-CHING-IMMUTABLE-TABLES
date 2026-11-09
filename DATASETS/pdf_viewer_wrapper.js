// Copyright 2012 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
import {E as EventTracker, a as assertInstanceof, b as assert, h as hasKeyModifiers, i as isRTL, c as isMac, g as getDeepActiveElement, d as isWindows, F as FocusOutlineManager, e as assertNotReachedCase, f as assertNotReached, A as AnnotationBrushType, T as TextTypeface, j as TextAlignment, k as TextStyle, P as PluginController, l as PluginControllerEventType, m as PromiseResolver, n as colorsEqual, o as TextAnnotationSource, p as getCss$J, C as CrRippleMixin, q as hexToColor, r as record, U as UserAction, s as getTextStyleForShortcut, t as hasCtrlModifierOnly, u as getInstance, v as colorToHex, w as hasCtrlModifier, x as blendHighlighterColorValue, y as getCss$K, z as debounceEnd, S as SaveToDriveState, B as SaveToDriveBubbleRequestType, D as AnnotationMode, G as FormFieldFocusType, H as FittingType, I as getCss$L, J as recordEnumeration, K as PdfViewerBaseElement, L as PdfHelpBubbleProxyImpl, M as shouldIgnoreKeyEvents, N as PostMessageDataType, O as convertSendKeyEventMessage, Q as convertDocumentDimensionsMessage, R as getSaveToDriveOpenInDriveUrl, V as getSaveToDriveManageStorageUrl, W as verifyPdfHeader, X as listenOnce, Y as convertLoadProgressMessage, Z as convertFormFocusChangeMessage} from "./shared.rollup.js";
export {_ as CrIconButtonElement, $ as GestureDetector, a2 as OpenPdfParamsParser, a6 as PAGE_SHADOW, a4 as SwipeDetector, a5 as SwipeDirection, a3 as ViewMode, a7 as Viewport, a8 as ZoomManager, a0 as recordFitTo, a1 as resetForTesting} from "./shared.rollup.js";
import {css, html, nothing, CrLitElement} from "chrome://resources/lit/v3_0/lit.rollup.js";
export {BrowserApi, ZoomBehavior} from "./browser_api.js";
import {loadTimeData} from "chrome://resources/js/load_time_data.js";
import {LoadState} from "./pdf_scripting_api.js";
import "chrome://resources/mojo/mojo/public/js/bindings.js";
const ACTIVE_CLASS = "focus-row-active";
class FocusRow {
    root;
    delegate;
    eventTracker = new EventTracker;
    boundary_;
    constructor(root, boundary, delegate) {
        this.root = root;
        this.boundary_ = boundary || document.documentElement;
        this.delegate = delegate
    }
    static isFocusable(element) {
        if (!element || element.disabled) {
            return false
        }
        let current = element;
        while (true) {
            assertInstanceof(current, Element);
            const style = window.getComputedStyle(current);
            if (style.visibility === "hidden" || style.display === "none") {
                return false
            }
            const parent = current.parentNode;
            if (!parent) {
                return false
            }
            if (parent === current.ownerDocument || parent instanceof DocumentFragment) {
                return true
            }
            current = parent
        }
    }
    static getFocusableElement(element) {
        const withFocusable = element;
        if (withFocusable.getFocusableElement) {
            return withFocusable.getFocusableElement()
        }
        return element
    }
    addItem(type, selectorOrElement) {
        assert(type);
        let element;
        if (typeof selectorOrElement === "string") {
            element = this.root.querySelector(selectorOrElement)
        } else {
            element = selectorOrElement
        }
        if (!element) {
            return false
        }
        element.setAttribute("focus-type", type);
        element.tabIndex = this.isActive() ? 0 : -1;
        this.eventTracker.add(element, "blur", this.onBlur_.bind(this));
        this.eventTracker.add(element, "focus", this.onFocus_.bind(this));
        this.eventTracker.add(element, "keydown", this.onKeydown_.bind(this));
        this.eventTracker.add(element, "mousedown", this.onMousedown_.bind(this));
        return true
    }
    destroy() {
        this.eventTracker.removeAll()
    }
    getCustomEquivalent(_sampleElement) {
        const focusable = this.getFirstFocusable();
        assert(focusable);
        return focusable
    }
    getElements() {
        return Array.from(this.root.querySelectorAll("[focus-type]")).map(FocusRow.getFocusableElement)
    }
    getEquivalentElement(sampleElement) {
        if (this.getFocusableElements().indexOf(sampleElement) >= 0) {
            return sampleElement
        }
        const sampleFocusType = this.getTypeForElement(sampleElement);
        if (sampleFocusType) {
            const sameType = this.getFirstFocusable(sampleFocusType);
            if (sameType) {
                return sameType
            }
        }
        return this.getCustomEquivalent(sampleElement)
    }
    getFirstFocusable(type) {
        const element = this.getFocusableElements().find((el => !type || el.getAttribute("focus-type") === type));
        return element || null
    }
    getFocusableElements() {
        return this.getElements().filter(FocusRow.isFocusable)
    }
    getTypeForElement(element) {
        return element.getAttribute("focus-type") || ""
    }
    isActive() {
        return this.root.classList.contains(ACTIVE_CLASS)
    }
    makeActive(active) {
        if (active === this.isActive()) {
            return
        }
        this.getElements().forEach((function(element) {
            element.tabIndex = active ? 0 : -1
        }
        ));
        this.root.classList.toggle(ACTIVE_CLASS, active)
    }
    onBlur_(e) {
        if (!this.boundary_.contains(e.relatedTarget)) {
            return
        }
        const currentTarget = e.currentTarget;
        if (this.getFocusableElements().indexOf(currentTarget) >= 0) {
            this.makeActive(false)
        }
    }
    onFocus_(e) {
        if (this.delegate) {
            this.delegate.onFocus(this, e)
        }
    }
    onMousedown_(e) {
        if (e.button) {
            return
        }
        const target = e.currentTarget;
        if (!target.disabled) {
            target.tabIndex = 0
        }
    }
    onKeydown_(e) {
        const elements = this.getFocusableElements();
        const currentElement = FocusRow.getFocusableElement(e.currentTarget);
        const elementIndex = elements.indexOf(currentElement);
        assert(elementIndex >= 0);
        if (this.delegate && this.delegate.onKeydown(this, e)) {
            return
        }
        const isShiftTab = !e.altKey && !e.ctrlKey && !e.metaKey && e.shiftKey && e.key === "Tab";
        if (hasKeyModifiers(e) && !isShiftTab) {
            return
        }
        let index = -1;
        let shouldStopPropagation = true;
        if (isShiftTab) {
            index = elementIndex - 1;
            if (index < 0) {
                return
            }
        } else if (e.key === "ArrowLeft") {
            index = elementIndex + (isRTL() ? 1 : -1)
        } else if (e.key === "ArrowRight") {
            index = elementIndex + (isRTL() ? -1 : 1)
        } else if (e.key === "Home") {
            index = 0
        } else if (e.key === "End") {
            index = elements.length - 1
        } else {
            shouldStopPropagation = false
        }
        const elementToFocus = elements[index];
        if (elementToFocus) {
            this.getEquivalentElement(elementToFocus).focus();
            e.preventDefault()
        }
        if (shouldStopPropagation) {
            e.stopPropagation()
        }
    }
}
let hideInk = false;
document.addEventListener("pointerdown", (function() {
    hideInk = true
}
), true);
document.addEventListener("keydown", (function() {
    hideInk = false
}
), true);
function focusWithoutInk(toFocus) {
    if (!("noink" in toFocus) || !hideInk) {
        toFocus.focus();
        return
    }
    const toFocusWithNoInk = toFocus;
    assert(document === toFocusWithNoInk.ownerDocument);
    const {noink: noink} = toFocusWithNoInk;
    toFocusWithNoInk.noink = true;
    toFocusWithNoInk.focus();
    toFocusWithNoInk.noink = noink
}
let instance$M = null;
function getCss$I() {
    return instance$M || (instance$M = [...[], css`:host{--cr-hairline:1px solid var(--color-menu-separator,var(--cr-fallback-color-divider));--cr-action-menu-disabled-item-color:var(--color-menu-item-foreground-disabled,var(--cr-fallback-color-disabled-foreground));--cr-action-menu-disabled-item-opacity:1;--cr-menu-background-color:var(--color-menu-background,var(--cr-fallback-color-surface));--cr-menu-background-focus-color:var(--cr-hover-background-color);--cr-menu-shadow:var(--cr-elevation-2);--cr-primary-text-color:var(--color-menu-item-foreground,var(--cr-fallback-color-on-surface))}:host dialog{background-color:var(--cr-menu-background-color);border:none;border-radius:var(--cr-menu-border-radius,4px);box-shadow:var(--cr-menu-shadow);margin:0;min-width:128px;outline:none;overflow:var(--cr-action-menu-overflow,auto);padding:0;position:absolute}:host([use-unbounded]) dialog{max-height:none;position:fixed}@media (forced-colors:active){:host dialog{border:var(--cr-border-hcm)}}:host dialog::backdrop{background-color:transparent}:host ::slotted(.dropdown-item){-webkit-tap-highlight-color:transparent;background:none;border:none;border-radius:0;box-sizing:border-box;color:var(--cr-primary-text-color);font:inherit;min-height:32px;padding:8px 24px;text-align:start;user-select:none;width:100%}:host ::slotted(.dropdown-item:not([hidden])){align-items:center;display:flex}:host ::slotted(.dropdown-item[disabled]){color:var(--cr-action-menu-disabled-item-color,var(--cr-primary-text-color));opacity:var(--cr-action-menu-disabled-item-opacity,0.65)}:host ::slotted(.dropdown-item:not([disabled])){cursor:pointer}:host ::slotted(.dropdown-item:focus){background-color:var(--cr-menu-background-focus-color);outline:none}:host dialog[open] ::slotted(.dropdown-item){user-select:auto}:host ::slotted(.dropdown-item:focus-visible){outline:solid 2px var(--cr-focus-outline-color);outline-offset:-2px}@media (forced-colors:active){:host ::slotted(.dropdown-item:focus){outline:var(--cr-focus-outline-hcm)}}.item-wrapper{outline:none;padding:var(--cr-action-menu-padding,8px 0)}`])
}
function getHtml$A() {
    return html`
<dialog id="dialog" part="dialog" @close="${this.onNativeDialogClose_}"
    @beforetoggle="${this.onDialogBeforetoggle_}"
    ?unbounded="${this.useUnbounded_}" role="application"
    aria-roledescription="${this.roleDescription || nothing}">
  <div id="wrapper" class="item-wrapper" role="menu" tabindex="-1"
      aria-label="${this.accessibilityLabel || nothing}">
    <slot id="contentNode" @slotchange="${this.onSlotchange_}"></slot>
  </div>
</dialog>`
}
function hasFocusoutOutside(e, element) {
    return !element || !element.contains(e.relatedTarget)
}
function isUnboundedSupported() {
    return "showUnboundedElement" in HTMLElement.prototype
}
var AnchorAlignment;
(function(AnchorAlignment) {
    AnchorAlignment[AnchorAlignment["BEFORE_START"] = -2] = "BEFORE_START";
    AnchorAlignment[AnchorAlignment["AFTER_START"] = -1] = "AFTER_START";
    AnchorAlignment[AnchorAlignment["CENTER"] = 0] = "CENTER";
    AnchorAlignment[AnchorAlignment["BEFORE_END"] = 1] = "BEFORE_END";
    AnchorAlignment[AnchorAlignment["AFTER_END"] = 2] = "AFTER_END"
}
)(AnchorAlignment || (AnchorAlignment = {}));
const DROPDOWN_ITEM_CLASS = "dropdown-item";
const SELECTABLE_DROPDOWN_ITEM_QUERY = `.${DROPDOWN_ITEM_CLASS}:not([hidden]):not([disabled])`;
const AFTER_END_OFFSET = 10;
function getStartPointWithAnchor(start, end, menuLength, anchorAlignment, min, max, unbounded=false) {
    let startPoint = 0;
    switch (anchorAlignment) {
    case AnchorAlignment.BEFORE_START:
        startPoint = start - menuLength;
        break;
    case AnchorAlignment.AFTER_START:
        startPoint = start;
        break;
    case AnchorAlignment.CENTER:
        startPoint = (start + end - menuLength) / 2;
        break;
    case AnchorAlignment.BEFORE_END:
        startPoint = end - menuLength;
        break;
    case AnchorAlignment.AFTER_END:
        startPoint = end;
        break;
    default:
        assertNotReachedCase()
    }
    if (unbounded) {
        const isForward = anchorAlignment === AnchorAlignment.AFTER_END || anchorAlignment === AnchorAlignment.AFTER_START;
        const isBackward = anchorAlignment === AnchorAlignment.BEFORE_START || anchorAlignment === AnchorAlignment.BEFORE_END;
        const spaceForward = max - end;
        const spaceBackward = start - min;
        if (isForward && Number.isFinite(max) && startPoint + menuLength > max) {
            if (spaceBackward >= menuLength || spaceBackward > spaceForward) {
                startPoint = anchorAlignment === AnchorAlignment.AFTER_END ? start - menuLength : end - menuLength
            }
        } else if (isBackward && Number.isFinite(min) && startPoint < min) {
            if (spaceForward >= menuLength || spaceForward > spaceBackward) {
                startPoint = anchorAlignment === AnchorAlignment.BEFORE_START ? end : start
            }
        } else if (anchorAlignment === AnchorAlignment.CENTER) {
            if (Number.isFinite(max) && startPoint + menuLength > max) {
                startPoint = max - menuLength
            }
            if (Number.isFinite(min) && startPoint < min) {
                startPoint = min
            }
        }
        return startPoint
    }
    if (startPoint + menuLength > max) {
        startPoint = end - menuLength
    }
    if (startPoint < min) {
        startPoint = start
    }
    startPoint = Math.max(min, Math.min(startPoint, max - menuLength));
    return startPoint
}
function getDefaultShowConfig() {
    return {
        top: 0,
        left: 0,
        height: 0,
        width: 0,
        anchorAlignmentX: AnchorAlignment.AFTER_START,
        anchorAlignmentY: AnchorAlignment.AFTER_START,
        minX: 0,
        minY: 0,
        maxX: 0,
        maxY: 0
    }
}
class CrActionMenuElement extends CrLitElement {
    static get is() {
        return "cr-action-menu"
    }
    static get styles() {
        return getCss$I()
    }
    render() {
        return getHtml$A.bind(this)()
    }
    static get properties() {
        return {
            accessibilityLabel: {
                type: String
            },
            autoReposition: {
                type: Boolean
            },
            autoCloseOnFocusout: {
                type: Boolean
            },
            open: {
                type: Boolean,
                notify: true
            },
            nonModal: {
                type: Boolean,
                reflect: true
            },
            roleDescription: {
                type: String
            },
            useUnbounded_: {
                type: Boolean
            }
        }
    }
    #accessibilityLabel_accessor_storage;
    get accessibilityLabel() {
        return this.#accessibilityLabel_accessor_storage
    }
    set accessibilityLabel(value) {
        this.#accessibilityLabel_accessor_storage = value
    }
    #autoReposition_accessor_storage = false;
    get autoReposition() {
        return this.#autoReposition_accessor_storage
    }
    set autoReposition(value) {
        this.#autoReposition_accessor_storage = value
    }
    #autoCloseOnFocusout_accessor_storage = false;
    get autoCloseOnFocusout() {
        return this.#autoCloseOnFocusout_accessor_storage
    }
    set autoCloseOnFocusout(value) {
        this.#autoCloseOnFocusout_accessor_storage = value
    }
    #open_accessor_storage = false;
    get open() {
        return this.#open_accessor_storage
    }
    set open(value) {
        this.#open_accessor_storage = value
    }
    #roleDescription_accessor_storage;
    get roleDescription() {
        return this.#roleDescription_accessor_storage
    }
    set roleDescription(value) {
        this.#roleDescription_accessor_storage = value
    }
    #nonModal_accessor_storage = false;
    get nonModal() {
        return this.#nonModal_accessor_storage
    }
    set nonModal(value) {
        this.#nonModal_accessor_storage = value
    }
    #useUnbounded__accessor_storage = false;
    get useUnbounded_() {
        return this.#useUnbounded__accessor_storage
    }
    set useUnbounded_(value) {
        this.#useUnbounded__accessor_storage = value
    }
    async setUnbounded() {
        if (!isUnboundedSupported()) {
            console.warn("CrActionMenu: Unbounded Element API is not supported in this " + "environment.");
            return false
        }
        this.useUnbounded_ = true;
        await this.updateComplete;
        return true
    }
    boundClose_ = null;
    resizeObserver_ = null;
    hasMousemoveListener_ = false;
    anchorElement_ = null;
    lastConfig_ = null;
    disconnectedCallback() {
        super.disconnectedCallback();
        this.removeListeners_()
    }
    firstUpdated() {
        this.addEventListener("keydown", this.onKeyDown_.bind(this));
        this.addEventListener("mouseover", this.onMouseover_);
        this.addEventListener("click", this.onClick_);
        this.addEventListener("focusout", this.onFocusout_.bind(this))
    }
    getDialog() {
        return this.$.dialog
    }
    getUnboundedDialog_() {
        return this.$.dialog
    }
    showUnboundedDialog_() {
        this.getUnboundedDialog_().showUnboundedElement().catch((err => this.handleUnboundedError_("showUnboundedElement", err)))
    }
    hideUnboundedDialog_() {
        this.getUnboundedDialog_().hideUnboundedElement().catch((err => this.handleUnboundedError_("hideUnboundedElement", err)))
    }
    handleUnboundedError_(operation, err) {
        if (err instanceof DOMException && err.name === "AbortError") {
            return
        }
        console.error(`${operation} failed:`, err)
    }
    removeListeners_() {
        window.removeEventListener("resize", this.boundClose_);
        window.removeEventListener("popstate", this.boundClose_);
        if (this.resizeObserver_) {
            this.resizeObserver_.disconnect();
            this.resizeObserver_ = null
        }
    }
    onFocusout_(e) {
        if (this.autoCloseOnFocusout && hasFocusoutOutside(e, this)) {
            this.close()
        }
    }
    onNativeDialogClose_(e) {
        if (e.target !== this.$.dialog) {
            return
        }
        this.fire("close")
    }
    onClick_(e) {
        if (e.target === this) {
            this.close();
            e.stopPropagation()
        }
    }
    onKeyDown_(e) {
        e.stopPropagation();
        if (e.key === "Tab" || e.key === "Escape") {
            this.close();
            if (e.key === "Tab") {
                this.fire("tabkeyclose", {
                    shiftKey: e.shiftKey
                })
            }
            e.preventDefault();
            return
        }
        if ((e.key !== "Enter" || isMac && e.ctrlKey) && e.key !== "ArrowUp" && e.key !== "ArrowDown") {
            return
        }
        const options = Array.from(this.querySelectorAll(SELECTABLE_DROPDOWN_ITEM_QUERY));
        if (options.length === 0) {
            return
        }
        const focused = getDeepActiveElement();
        const index = options.findIndex((option => FocusRow.getFocusableElement(option) === focused));
        if (e.key === "Enter") {
            if (index !== -1) {
                return
            }
            if (isWindows || isMac) {
                this.close();
                e.preventDefault();
                return
            }
        }
        e.preventDefault();
        this.updateFocus_(options, index, e.key !== "ArrowUp");
        if (!this.hasMousemoveListener_) {
            this.hasMousemoveListener_ = true;
            this.addEventListener("mousemove", (e => {
                this.onMouseover_(e);
                this.hasMousemoveListener_ = false
            }
            ), {
                once: true
            })
        }
    }
    focusElement_(el) {
        el.focus({
            preventScroll: this.useUnbounded_
        })
    }
    onMouseover_(e) {
        const item = e.composedPath().find((el => el.matches && el.matches(SELECTABLE_DROPDOWN_ITEM_QUERY)));
        this.focusElement_(item || this.$.wrapper)
    }
    updateFocus_(options, focusedIndex, next) {
        const numOptions = options.length;
        assert(numOptions > 0);
        let index;
        if (focusedIndex === -1) {
            index = next ? 0 : numOptions - 1
        } else {
            const delta = next ? 1 : -1;
            index = (numOptions + focusedIndex + delta) % numOptions
        }
        this.focusElement_(options[index])
    }
    close(unboundedAlreadyDismissed=false) {
        if (!this.open) {
            return
        }
        this.open = false;
        if (this.useUnbounded_ && !unboundedAlreadyDismissed) {
            this.hideUnboundedDialog_()
        }
        this.removeListeners_();
        this.$.dialog.close();
        if (this.anchorElement_) {
            assert(this.anchorElement_);
            focusWithoutInk(this.anchorElement_);
            this.anchorElement_ = null
        }
        if (this.lastConfig_) {
            this.lastConfig_ = null
        }
    }
    showAt(anchorElement, config) {
        this.anchorElement_ = anchorElement;
        this.anchorElement_.scrollIntoViewIfNeeded();
        const rect = this.anchorElement_.getBoundingClientRect();
        let height = rect.height;
        if (config && !config.noOffset && config.anchorAlignmentY === AnchorAlignment.AFTER_END) {
            height -= AFTER_END_OFFSET
        }
        this.showAtPosition(Object.assign({
            top: rect.top,
            left: rect.left,
            height: height,
            width: rect.width,
            anchorAlignmentX: AnchorAlignment.BEFORE_END
        }, config));
        this.focusElement_(this.$.wrapper)
    }
    showAtPosition(config) {
        const doc = document.scrollingElement;
        const scrollLeft = doc.scrollLeft;
        const scrollTop = doc.scrollTop;
        this.resetStyle_();
        this.nonModal ? this.$.dialog.show() : this.$.dialog.showModal();
        this.open = true;
        if (this.useUnbounded_) {
            this.positionDialog_(config);
            this.showUnboundedDialog_()
        } else {
            config.top += scrollTop;
            config.left += scrollLeft;
            this.positionDialog_(Object.assign({
                minX: scrollLeft,
                minY: scrollTop,
                maxX: scrollLeft + doc.clientWidth,
                maxY: scrollTop + doc.clientHeight
            }, config))
        }
        doc.scrollTop = scrollTop;
        doc.scrollLeft = scrollLeft;
        this.addListeners_();
        const openedByKey = FocusOutlineManager.forDocument(document).visible;
        if (openedByKey) {
            const firstSelectableItem = this.querySelector(SELECTABLE_DROPDOWN_ITEM_QUERY);
            if (firstSelectableItem) {
                requestAnimationFrame(( () => {
                    this.focusElement_(firstSelectableItem)
                }
                ))
            }
        }
    }
    resetStyle_() {
        this.$.dialog.style.left = "";
        this.$.dialog.style.right = "";
        this.$.dialog.style.top = "0"
    }
    positionDialog_(config) {
        this.lastConfig_ = config;
        const c = Object.assign(getDefaultShowConfig(), config);
        if (this.useUnbounded_) {
            const screenLeft = window.screenX;
            const screenTop = window.screenY;
            const screenWidth = window.screen.availWidth;
            const screenHeight = window.screen.availHeight;
            if (config.minX === undefined) {
                c.minX = -screenLeft
            }
            if (config.minY === undefined) {
                c.minY = -screenTop
            }
            if (config.maxX === undefined) {
                c.maxX = screenWidth - screenLeft
            }
            if (config.maxY === undefined) {
                c.maxY = screenHeight - screenTop
            }
        }
        const top = c.top;
        const left = c.left;
        const bottom = top + c.height;
        const right = left + c.width;
        const rtl = getComputedStyle(this).direction === "rtl";
        if (rtl) {
            c.anchorAlignmentX *= -1
        }
        const offsetWidth = this.$.dialog.offsetWidth;
        const menuLeft = getStartPointWithAnchor(left, right, offsetWidth, c.anchorAlignmentX, c.minX, c.maxX, this.useUnbounded_);
        if (rtl) {
            const menuRight = document.scrollingElement.clientWidth - menuLeft - offsetWidth;
            this.$.dialog.style.right = menuRight + "px"
        } else {
            this.$.dialog.style.left = menuLeft + "px"
        }
        const menuTop = getStartPointWithAnchor(top, bottom, this.$.dialog.offsetHeight, c.anchorAlignmentY, c.minY, c.maxY, this.useUnbounded_);
        this.$.dialog.style.top = menuTop + "px"
    }
    onSlotchange_() {
        for (const node of this.$.contentNode.assignedElements({
            flatten: true
        })) {
            if (node.classList.contains(DROPDOWN_ITEM_CLASS) && !node.getAttribute("role")) {
                node.setAttribute("role", "menuitem")
            }
        }
    }
    onDialogBeforetoggle_(e) {
        if (!this.useUnbounded_) {
            return
        }
        const toggleEvent = e;
        if (toggleEvent.newState === "closed" && this.open) {
            this.close(true)
        }
    }
    addListeners_() {
        this.boundClose_ = this.boundClose_ || ( () => {
            if (this.$.dialog.open) {
                this.close()
            }
        }
        );
        window.addEventListener("resize", this.boundClose_);
        window.addEventListener("popstate", this.boundClose_);
        if (this.autoReposition) {
            this.resizeObserver_ = new ResizeObserver(( () => {
                if (this.lastConfig_) {
                    this.positionDialog_(this.lastConfig_);
                    this.fire("cr-action-menu-repositioned")
                }
            }
            ));
            this.resizeObserver_.observe(this.$.dialog)
        }
    }
}
customElements.define(CrActionMenuElement.is, CrActionMenuElement);
class BeforeUnloadProxyImpl {
    preventDefault(event) {
        event.preventDefault()
    }
    static getInstance() {
        return instance$L || (instance$L = new BeforeUnloadProxyImpl)
    }
    static setInstance(obj) {
        instance$L = obj
    }
}
let instance$L = null;
function convertRotatedCoordinates(rect, oldRotations, newRotations, newPageWidth, newPageHeight) {
    const pageWidthNR = newRotations % 2 === 0 ? newPageWidth : newPageHeight;
    const pageHeightNR = newRotations % 2 === 0 ? newPageHeight : newPageWidth;
    const nonRotated = {
        locationX: rect.locationX,
        locationY: rect.locationY,
        width: oldRotations % 2 === 0 ? rect.width : rect.height,
        height: oldRotations % 2 === 0 ? rect.height : rect.width
    };
    switch (oldRotations % 4) {
    case 0:
        break;
    case 1:
        nonRotated.locationX = rect.locationY;
        nonRotated.locationY = pageHeightNR - rect.locationX - rect.width;
        break;
    case 2:
        nonRotated.locationX = pageWidthNR - rect.locationX - rect.width;
        nonRotated.locationY = pageHeightNR - rect.locationY - rect.height;
        break;
    case 3:
        nonRotated.locationX = pageWidthNR - rect.locationY - rect.height;
        nonRotated.locationY = rect.locationX;
        break;
    default:
        assertNotReached()
    }
    const newRotated = {
        locationX: nonRotated.locationX,
        locationY: nonRotated.locationY,
        width: newRotations % 2 === 0 ? nonRotated.width : nonRotated.height,
        height: newRotations % 2 === 0 ? nonRotated.height : nonRotated.width
    };
    switch (newRotations % 4) {
    case 0:
        break;
    case 1:
        newRotated.locationX = pageHeightNR - nonRotated.locationY - nonRotated.height;
        newRotated.locationY = nonRotated.locationX;
        break;
    case 2:
        newRotated.locationX = pageWidthNR - nonRotated.locationX - nonRotated.width;
        newRotated.locationY = pageHeightNR - nonRotated.locationY - nonRotated.height;
        break;
    case 3:
        newRotated.locationX = nonRotated.locationY;
        newRotated.locationY = pageWidthNR - nonRotated.locationX - nonRotated.width;
        break;
    default:
        assertNotReached()
    }
    return newRotated
}
function pageToScreenCoordinates(pageIndex, pageRect, viewport) {
    const pageDimensions = viewport.getPageScreenRect(pageIndex);
    const zoom = viewport.getZoom();
    const zoomed = {
        locationX: pageRect.locationX * zoom,
        locationY: pageRect.locationY * zoom,
        width: pageRect.width * zoom,
        height: pageRect.height * zoom
    };
    const rotated = convertRotatedCoordinates(zoomed, 0, viewport.getClockwiseRotations(), pageDimensions.width, pageDimensions.height);
    return {
        locationX: rotated.locationX + pageDimensions.x,
        locationY: rotated.locationY + pageDimensions.y,
        height: rotated.height,
        width: rotated.width
    }
}
function screenToPageCoordinates(pageIndex, screenRect, viewport) {
    const zoom = viewport.getZoom();
    const pageDimensions = viewport.getPageScreenRect(pageIndex);
    const noOffset = {
        locationX: screenRect.locationX - pageDimensions.x,
        locationY: screenRect.locationY - pageDimensions.y,
        width: screenRect.width,
        height: screenRect.height
    };
    const rotations = viewport.getClockwiseRotations();
    const pageWidth = rotations % 2 === 0 ? pageDimensions.width : pageDimensions.height;
    const pageHeight = rotations % 2 === 0 ? pageDimensions.height : pageDimensions.width;
    const noRotation = convertRotatedCoordinates(noOffset, rotations, 0, pageWidth, pageHeight);
    return {
        height: noRotation.height / zoom,
        locationX: noRotation.locationX / zoom,
        locationY: noRotation.locationY / zoom,
        width: noRotation.width / zoom
    }
}
class UndoRedoStack {
    stack_ = [];
    pointer_ = -1;
    savedPointer_ = -1;
    savingPointer_ = -1;
    eventTarget_;
    constructor(eventTarget) {
        this.eventTarget_ = eventTarget
    }
    dispatchStateChanged_() {
        const detail = {
            canUndo: this.canUndo(),
            canRedo: this.canRedo(),
            hasUnsavedEdits: this.isDirty()
        };
        this.eventTarget_.dispatchEvent(new CustomEvent("undo-redo-state-changed",{
            detail: detail
        }))
    }
    push(state) {
        this.stack_.splice(this.pointer_ + 1);
        this.stack_.push(state);
        if (this.savedPointer_ > this.pointer_) {
            this.savedPointer_ = -1
        }
        if (this.savingPointer_ > this.pointer_) {
            this.savingPointer_ = -1
        }
        this.pointer_++;
        this.dispatchStateChanged_()
    }
    undo() {
        if (!this.canUndo()) {
            return null
        }
        const state = this.stack_[this.pointer_];
        this.pointer_--;
        this.dispatchStateChanged_();
        return state
    }
    redo() {
        if (!this.canRedo()) {
            return null
        }
        this.pointer_++;
        const state = this.stack_[this.pointer_];
        this.dispatchStateChanged_();
        return state
    }
    canUndo() {
        return this.pointer_ >= 0
    }
    canRedo() {
        return this.pointer_ < this.stack_.length - 1
    }
    initiateSave() {
        assert(this.savingPointer_ === -1);
        this.savingPointer_ = this.pointer_
    }
    setSaved() {
        const changed = this.savedPointer_ !== this.savingPointer_;
        this.savedPointer_ = this.savingPointer_;
        this.savingPointer_ = -1;
        if (changed) {
            this.dispatchStateChanged_()
        }
    }
    cancelSave() {
        this.savingPointer_ = -1
    }
    isDirty() {
        return this.pointer_ !== this.savedPointer_
    }
    resetForTesting() {
        this.stack_ = [];
        this.pointer_ = -1;
        this.savedPointer_ = -1;
        this.savingPointer_ = -1;
        this.dispatchStateChanged_()
    }
}
const DEFAULT_TEXTBOX_WIDTH = 222;
const MIN_TEXTBOX_SIZE_PX = 24;
function stylesEqual(style1, style2) {
    return style1.bold === style2.bold && style1.italic === style2.italic && style1.strikethrough === style2.strikethrough && style1.underline === style2.underline
}
function getClampedLocation(location, width, height, pageDimensions) {
    const maxX = pageDimensions.x + pageDimensions.width - width;
    const maxY = pageDimensions.y + pageDimensions.height - height;
    return {
        x: Math.max(pageDimensions.x, Math.min(location.x, maxX)),
        y: Math.max(pageDimensions.y, Math.min(location.y, maxY))
    }
}
class Ink2Manager extends EventTarget {
    brush_ = {
        type: AnnotationBrushType.PEN
    };
    stack_ = new UndoRedoStack(this);
    listener_;
    annotations_ = new Map;
    attributes_ = {
        typeface: TextTypeface.SANS_SERIF,
        size: 12,
        color: {
            r: 0,
            g: 0,
            b: 0
        },
        alignment: TextAlignment.LEFT,
        styles: {
            [TextStyle.BOLD]: false,
            [TextStyle.ITALIC]: false,
            [TextStyle.STRIKETHROUGH]: false,
            [TextStyle.UNDERLINE]: false
        }
    };
    brushResolver_ = null;
    existingAnnotationAttributes_ = null;
    clipboardAnnotation_ = null;
    isCutAnnotation_ = false;
    pastedPageRects_ = new Map;
    pluginController_ = PluginController.getInstance();
    textResolver_ = null;
    viewport_ = null;
    nextAnnotationId_ = 0;
    knownFontIds_ = [];
    constructor() {
        super();
        this.listener_ = this.handleFinishInkStroke_.bind(this);
        this.pluginController_.getEventTarget().addEventListener(PluginControllerEventType.FINISH_INK_STROKE, this.listener_)
    }
    destroy() {
        this.pluginController_.getEventTarget().removeEventListener(PluginControllerEventType.FINISH_INK_STROKE, this.listener_)
    }
    setViewport(viewport) {
        this.viewport_ = viewport
    }
    get annotations() {
        return this.annotations_
    }
    resetStackForTesting() {
        this.stack_.resetForTesting()
    }
    initializeTextAnnotation(location, onlyExisting=false) {
        assert(this.isTextInitializationComplete());
        assert(this.viewport_);
        const isMouse = !!location;
        const page = location ? this.viewport_.getPageAtPoint(location) : this.viewport_.getMostVisiblePage();
        if (page === -1) {
            return false
        }
        if (location) {
            const annotationsMap = this.annotations_.get(page);
            if (annotationsMap && annotationsMap.size > 0) {
                let candidate = null;
                let candidateScreenRect = null;
                for (const annotation of annotationsMap.values()) {
                    const screenRect = pageToScreenCoordinates(page, annotation.textBoxRect, this.viewport_);
                    if (location.x >= screenRect.locationX && location.x <= screenRect.locationX + screenRect.width && location.y >= screenRect.locationY && location.y <= screenRect.locationY + screenRect.height) {
                        if (!candidate || annotation.id > candidate.id) {
                            candidate = annotation;
                            candidateScreenRect = screenRect
                        }
                    }
                }
                if (candidate) {
                    assert(candidateScreenRect);
                    return this.activateAnnotation_(candidate, candidateScreenRect)
                }
            }
        }
        if (onlyExisting) {
            return false
        }
        const pageDimensions = this.viewport_.getPageScreenRect(page);
        const newBoxHeight = Math.max(MIN_TEXTBOX_SIZE_PX, Math.ceil(1.2 * this.attributes_.size * this.viewport_.getZoom()));
        let newBoxWidth = Math.min(DEFAULT_TEXTBOX_WIDTH, Math.max(MIN_TEXTBOX_SIZE_PX, pageDimensions.width));
        if (!location) {
            const minX = Math.max(pageDimensions.x, 0);
            const minY = Math.max(pageDimensions.y, 0);
            const maxX = Math.min(pageDimensions.x + pageDimensions.width, this.viewport_.size.width);
            const maxY = Math.min(pageDimensions.y + pageDimensions.height, this.viewport_.size.height);
            location = {
                x: Math.max(0, (minX + maxX) / 2 - newBoxWidth / 2),
                y: Math.max(0, (minY + maxY) / 2 - newBoxHeight / 2)
            }
        }
        if (isMouse) {
            location.y = location.y - this.attributes_.size * this.viewport_.getZoom() / 2
        }
        const minWidth = 2 * MIN_TEXTBOX_SIZE_PX;
        if (pageDimensions.width < minWidth || pageDimensions.height < newBoxHeight) {
            return false
        }
        location = getClampedLocation(location, minWidth, newBoxHeight, pageDimensions);
        newBoxWidth = Math.min(newBoxWidth, pageDimensions.x + pageDimensions.width - location.x);
        const viewportRotations = this.viewport_.getClockwiseRotations();
        const annotation = {
            id: this.nextAnnotationId_,
            mojoTextInfo: new ArrayBuffer(0),
            pageIndex: page,
            pdfZoom: this.viewport_.getZoom(),
            text: "",
            textAttributes: structuredClone(this.attributes_),
            textBoxRect: {
                height: newBoxHeight,
                locationX: location.x,
                locationY: location.y,
                width: newBoxWidth
            },
            textOrientation: (4 - viewportRotations) % 4,
            viewportOrientation: viewportRotations
        };
        this.nextAnnotationId_++;
        this.initializeTextBox_(annotation, pageDimensions, false);
        return true
    }
    activateAnnotationById(id) {
        assert(this.isTextInitializationComplete());
        for (const pageAnnotations of this.annotations_.values()) {
            const annotation = pageAnnotations.get(id);
            if (annotation) {
                assert(this.viewport_);
                const screenRect = pageToScreenCoordinates(annotation.pageIndex, annotation.textBoxRect, this.viewport_);
                return this.activateAnnotation_(annotation, screenRect)
            }
        }
        return false
    }
    activateAnnotation_(annotation, screenRect) {
        assert(this.viewport_);
        const pageDimensions = this.viewport_.getPageScreenRect(annotation.pageIndex);
        if (!pageDimensions) {
            return false
        }
        const annotationToActivate = structuredClone(annotation);
        annotationToActivate.textBoxRect = screenRect;
        this.initializeTextBox_(annotationToActivate, pageDimensions, false, true);
        this.pluginController_.editTextAnnotation(annotation.id);
        return true
    }
    initializeTextBox_(annotation, pageDimensions, isPaste, isExisting=false) {
        this.existingAnnotationAttributes_ = isPaste || isExisting ? structuredClone(annotation.textAttributes) : null;
        this.dispatchEvent(new CustomEvent("initialize-text-box",{
            detail: {
                annotation: annotation,
                pageDimensions: pageDimensions,
                isPaste: isPaste
            }
        }));
        this.fireAttributesChanged_()
    }
    saveAnnotationToClipboard(annotation, isCut=false) {
        assert(annotation.text !== "");
        this.clipboardAnnotation_ = structuredClone(annotation);
        this.isCutAnnotation_ = isCut;
        this.pastedPageRects_.clear();
        if (!isCut) {
            this.pastedPageRects_.set(annotation.pageIndex, annotation.textBoxRect)
        }
        this.dispatchEvent(new CustomEvent("saved-annotation-to-clipboard-for-testing",{
            detail: {
                annotation: this.clipboardAnnotation_,
                isCut: this.isCutAnnotation_
            }
        }))
    }
    getPastedAnnotationPosition_() {
        assert(this.clipboardAnnotation_);
        assert(this.viewport_);
        let page = this.viewport_.getMostVisiblePage();
        let pageDimensions = this.viewport_.getPageScreenRect(page);
        if (pageDimensions.height === 0 || pageDimensions.width === 0) {
            return null
        }
        if (page !== this.clipboardAnnotation_.pageIndex) {
            const screenRectOnPage = pageToScreenCoordinates(page, this.clipboardAnnotation_.textBoxRect, this.viewport_);
            if (screenRectOnPage.width > pageDimensions.width || screenRectOnPage.height > pageDimensions.height) {
                page = this.clipboardAnnotation_.pageIndex;
                pageDimensions = this.viewport_.getPageScreenRect(page);
                if (pageDimensions.height === 0 || pageDimensions.width === 0) {
                    return null
                }
            }
        }
        const lastRect = this.pastedPageRects_.get(page);
        const offset = lastRect ? 10 : 0;
        const basePageRect = lastRect ?? this.clipboardAnnotation_.textBoxRect;
        const screenRect = pageToScreenCoordinates(page, basePageRect, this.viewport_);
        const location = getClampedLocation({
            x: screenRect.locationX + offset,
            y: screenRect.locationY + offset
        }, screenRect.width, screenRect.height, pageDimensions);
        const textBoxRect = {
            height: screenRect.height,
            locationX: location.x,
            locationY: location.y,
            width: screenRect.width
        };
        return {
            page: page,
            pageDimensions: pageDimensions,
            textBoxRect: textBoxRect
        }
    }
    pasteAnnotation() {
        assert(this.isTextInitializationComplete());
        assert(this.viewport_);
        if (!this.clipboardAnnotation_) {
            return false
        }
        const position = this.getPastedAnnotationPosition_();
        if (!position) {
            return false
        }
        const {page: page, pageDimensions: pageDimensions, textBoxRect: textBoxRect} = position;
        const viewportRotations = this.viewport_.getClockwiseRotations();
        let id;
        if (this.isCutAnnotation_) {
            id = this.clipboardAnnotation_.id;
            this.nextAnnotationId_ = Math.max(this.nextAnnotationId_, id + 1);
            this.isCutAnnotation_ = false
        } else {
            id = this.nextAnnotationId_++
        }
        const annotation = {
            id: id,
            mojoTextInfo: this.clipboardAnnotation_.mojoTextInfo,
            pageIndex: page,
            pdfZoom: this.viewport_.getZoom(),
            text: this.clipboardAnnotation_.text,
            textAttributes: structuredClone(this.clipboardAnnotation_.textAttributes),
            textBoxRect: textBoxRect,
            textOrientation: this.clipboardAnnotation_.textOrientation,
            viewportOrientation: viewportRotations
        };
        const pageRect = screenToPageCoordinates(page, textBoxRect, this.viewport_);
        this.pastedPageRects_.set(page, pageRect);
        this.initializeTextBox_(annotation, pageDimensions, true);
        return true
    }
    isInitializationStarted() {
        return this.brushResolver_ !== null
    }
    isTextInitializationComplete() {
        return this.textResolver_ !== null && this.textResolver_.isFulfilled
    }
    isInitializationComplete() {
        return this.isInitializationStarted() && this.brushResolver_.isFulfilled
    }
    getCurrentBrush() {
        assert(this.isInitializationComplete());
        return this.brush_
    }
    getCurrentTextAttributes() {
        return this.existingAnnotationAttributes_ ? this.existingAnnotationAttributes_ : this.attributes_
    }
    initializeBrush() {
        assert(this.brushResolver_ === null);
        this.brushResolver_ = new PromiseResolver;
        this.pluginController_.getAnnotationBrush().then((defaultBrushMessage => {
            this.setAnnotationBrush_(defaultBrushMessage.data);
            assert(this.brushResolver_);
            this.brushResolver_.resolve()
        }
        ));
        return this.brushResolver_.promise
    }
    initializeTextAnnotations() {
        if (this.textResolver_) {
            return this.textResolver_.promise
        }
        this.textResolver_ = new PromiseResolver;
        this.pluginController_.getAllTextAnnotations().then((message => {
            message.annotations.forEach((annotation => {
                let pageMap = this.annotations_.get(annotation.pageIndex);
                if (!pageMap) {
                    pageMap = new Map;
                    this.annotations_.set(annotation.pageIndex, pageMap)
                }
                pageMap.set(annotation.id, annotation);
                this.nextAnnotationId_ = Math.max(this.nextAnnotationId_, annotation.id + 1)
            }
            ));
            this.textResolver_.resolve();
            this.dispatchEvent(new CustomEvent("annotations-updated"))
        }
        ));
        return this.textResolver_.promise
    }
    setBrushColor(color) {
        assert(this.brush_.type !== AnnotationBrushType.ERASER);
        if (this.brush_.color === color) {
            return
        }
        this.brush_.color = color;
        this.fireBrushChanged_();
        this.setAnnotationBrushInPlugin_()
    }
    setBrushSize(size) {
        if (this.brush_.size === size) {
            return
        }
        this.brush_.size = size;
        this.fireBrushChanged_();
        this.setAnnotationBrushInPlugin_()
    }
    async setBrushType(type) {
        if (this.brush_.type === type) {
            return
        }
        const brushMessage = await this.pluginController_.getAnnotationBrush(type);
        this.setAnnotationBrush_(brushMessage.data);
        this.setAnnotationBrushInPlugin_()
    }
    setTextTypeface(typeface) {
        const current = this.getCurrentTextAttributes();
        if (current.typeface === typeface) {
            return
        }
        current.typeface = typeface;
        this.fireAttributesChanged_()
    }
    setTextSize(size) {
        const current = this.getCurrentTextAttributes();
        if (current.size === size) {
            return
        }
        current.size = size;
        this.fireAttributesChanged_()
    }
    setTextColor(color) {
        const current = this.getCurrentTextAttributes();
        if (colorsEqual(current.color, color)) {
            return
        }
        current.color = color;
        this.fireAttributesChanged_()
    }
    setTextAlignment(alignment) {
        const current = this.getCurrentTextAttributes();
        if (current.alignment === alignment) {
            return
        }
        current.alignment = alignment;
        this.fireAttributesChanged_()
    }
    setTextStyles(styles) {
        const current = this.getCurrentTextAttributes();
        if (stylesEqual(current.styles, styles)) {
            return
        }
        current.styles = styles;
        this.fireAttributesChanged_()
    }
    toggleTextStyle(style) {
        const current = this.getCurrentTextAttributes();
        const newStyles = Object.assign({}, current.styles);
        newStyles[style] = !newStyles[style];
        this.setTextStyles(newStyles)
    }
    getKnownFontIds() {
        return [...this.knownFontIds_]
    }
    addKnownFontId(id) {
        assert(!this.knownFontIds_.includes(id));
        this.knownFontIds_.push(id)
    }
    updateStoredAnnotation_(annotation) {
        let pageAnnotations = this.annotations_.get(annotation.pageIndex);
        if (!pageAnnotations) {
            pageAnnotations = new Map;
            this.annotations_.set(annotation.pageIndex, pageAnnotations)
        }
        const previous = pageAnnotations.get(annotation.id);
        if (annotation.text === "") {
            assert(pageAnnotations.delete(annotation.id))
        } else {
            pageAnnotations.set(annotation.id, annotation)
        }
        return previous || null
    }
    commitTextAnnotation(annotation, isEdited, newTypefaces) {
        assert(this.viewport_);
        annotation.textBoxRect = screenToPageCoordinates(annotation.pageIndex, annotation.textBoxRect, this.viewport_);
        if (isEdited) {
            const before = this.updateStoredAnnotation_(annotation);
            const after = annotation.text === "" ? null : structuredClone(annotation);
            if (before !== null || after !== null) {
                this.stack_.push({
                    type: "text",
                    before: before,
                    after: after
                })
            }
        }
        const messageData = {
            ...annotation,
            isEdited: isEdited,
            newTypefaces: newTypefaces,
            source: TextAnnotationSource.USER
        };
        this.pluginController_.finishTextAnnotation(messageData);
        this.existingAnnotationAttributes_ = null;
        this.dispatchEvent(new CustomEvent("annotations-updated"));
        this.fireAttributesChanged_()
    }
    setAnnotationBrush_(brush) {
        this.brush_ = brush;
        this.fireBrushChanged_()
    }
    setAnnotationBrushInPlugin_() {
        this.pluginController_.setAnnotationBrush(this.brush_)
    }
    fireBrushChanged_() {
        this.dispatchEvent(new CustomEvent("brush-changed",{
            detail: this.brush_
        }))
    }
    fireAttributesChanged_() {
        this.dispatchEvent(new CustomEvent("attributes-changed",{
            detail: structuredClone(this.getCurrentTextAttributes())
        }))
    }
    handleFinishInkStroke_(e) {
        if (e.detail) {
            this.stack_.push({
                type: "ink"
            })
        }
    }
    undo() {
        const state = this.stack_.undo();
        if (!state) {
            return
        }
        if (state.type === "text") {
            this.applyTextUndoRedo_(state.before, state.after, TextAnnotationSource.UNDO)
        }
        this.pluginController_.undo()
    }
    redo() {
        const state = this.stack_.redo();
        if (!state) {
            return
        }
        if (state.type === "text") {
            this.applyTextUndoRedo_(state.after, state.before, TextAnnotationSource.REDO)
        }
        this.pluginController_.redo()
    }
    applyTextUndoRedo_(update, previous, source) {
        const isDeletion = update === null;
        const annotation = isDeletion ? previous : update;
        assert(annotation);
        assert(this.viewport_);
        const pageAnnotations = this.annotations_.get(annotation.pageIndex);
        assert(pageAnnotations);
        if (isDeletion) {
            pageAnnotations.delete(annotation.id)
        } else {
            pageAnnotations.set(annotation.id, annotation)
        }
        const messageData = {
            ...annotation,
            isEdited: true,
            newTypefaces: [],
            source: source
        };
        if (isDeletion) {
            messageData.text = ""
        }
        this.pluginController_.finishTextAnnotation(messageData);
        this.dispatchEvent(new CustomEvent("annotations-updated"))
    }
    initiateSave() {
        this.stack_.initiateSave()
    }
    cancelSave() {
        this.stack_.cancelSave()
    }
    saved() {
        this.stack_.setSaved()
    }
    static getInstance() {
        return instance$K || (instance$K = new Ink2Manager)
    }
    static setInstance(obj) {
        if (instance$K) {
            instance$K.destroy()
        }
        instance$K = obj
    }
}
let instance$K = null;
let instance$J = null;
function getCss$H() {
    return instance$J || (instance$J = [...[], css`:host{--cr-radio-button-checked-color:var(--color-radio-button-foreground-checked,var(--cr-fallback-color-primary));--cr-radio-button-checked-ripple-color:var(--cr-active-background-color);--cr-radio-button-ink-size:32px;--cr-radio-button-size:16px;--cr-radio-button-unchecked-color:var(--color-radio-button-foreground-unchecked,var(--cr-fallback-color-outline));--cr-radio-button-unchecked-ripple-color:var(--cr-active-background-color);--ink-to-circle:calc((var(--cr-radio-button-ink-size) - var(--cr-radio-button-size)) / 2);align-items:center;display:flex;flex-shrink:0;gap:var(--cr-radio-button-label-spacing,20px);outline:none}:host-context(html:not([webui-refresh-2026])){@media (prefers-color-scheme:dark){:host{--cr-radio-button-checked-color:var(--google-blue-300);--cr-radio-button-checked-ripple-color:rgba(var(--google-blue-300-rgb),.4);--cr-radio-button-unchecked-color:var(--google-grey-500);--cr-radio-button-unchecked-ripple-color:rgba(var(--google-grey-300-rgb),.4)}}}@media (forced-colors:active){:host{--cr-radio-button-checked-color:SelectedItem;--cr-radio-button-unchecked-color:CanvasText}.disc-wrapper{forced-color-adjust:none}}:host([disabled]){opacity:1;pointer-events:none;--cr-radio-button-checked-color:var(--color-radio-foreground-disabled,var(--cr-fallback-color-disabled-foreground));--cr-radio-button-unchecked-color:var(--color-radio-foreground-disabled,var(--cr-fallback-color-disabled-foreground))}:host(:not([disabled])){cursor:pointer}:host(.label-first){flex-direction:row-reverse}#labelWrapper{flex:1}:host([disabled]) #labelWrapper{opacity:var(--cr-disabled-opacity)}#label{color:inherit}:host([hide-label-text]) #label{clip:rect(0,0,0,0);display:block;position:fixed}.disc-border,.disc,.disc-wrapper,cr-ripple,paper-ripple{border-radius:50%}.disc-wrapper{height:var(--cr-radio-button-size);margin-block-start:var(--cr-radio-button-disc-margin-block-start,0);position:relative;width:var(--cr-radio-button-size)}.disc-border,.disc{box-sizing:border-box;height:var(--cr-radio-button-size);width:var(--cr-radio-button-size)}.disc-border{border:2px solid var(--cr-radio-button-unchecked-color)}:host([checked]) .disc-border{border-color:var(--cr-radio-button-checked-color)}#button:focus{outline:none}.disc{background-color:transparent;position:absolute;top:0;transform:scale(0);transition:border-color 200ms,transform 200ms}:host([checked]) .disc{background-color:var(--cr-radio-button-checked-color);transform:scale(0.5)}#overlay{border-radius:50%;box-sizing:border-box;display:none;height:var(--cr-radio-button-ink-size);left:50%;pointer-events:none;position:absolute;top:50%;transform:translate(-50%,-50%);width:var(--cr-radio-button-ink-size)}#button:hover #overlay{background-color:var(--cr-hover-background-color);display:block}#button:focus-visible #overlay{border:2px solid var(--cr-focus-outline-color);display:block}cr-ripple,paper-ripple{--paper-ripple-opacity:1;color:var(--cr-radio-button-unchecked-ripple-color);height:var(--cr-radio-button-ink-size);left:calc(-1 * var(--ink-to-circle));pointer-events:none;position:absolute;top:calc(-1 * var(--ink-to-circle));transition:color linear 80ms;width:var(--cr-radio-button-ink-size)}:host-context([dir=rtl]) cr-ripple,:host-context([dir=rtl]) paper-ripple{left:auto;right:calc(-1 * var(--ink-to-circle))}:host([checked]) cr-ripple,:host([checked]) paper-ripple{color:var(--cr-radio-button-checked-ripple-color)}`])
}
let instance$I = null;
function getCss$G() {
    return instance$I || (instance$I = [...[getCss$H(), getCss$J()], css``])
}
function getHtml$z() {
    return html`
<div aria-checked="${this.getAriaChecked()}" aria-describedby="slotted-content"
    aria-disabled="${this.getAriaDisabled()}" aria-labelledby="label"
    class="disc-wrapper" id="button" role="radio"
    tabindex="${this.getButtonTabIndex()}" @keydown="${this.onInputKeydown}">
  <div class="disc-border"></div>
  <div class="disc"></div>
  <div id="overlay"></div>
</div>

<div id="labelWrapper">
  <span id="label" ?hidden="${!this.label}" aria-hidden="true">
    ${this.label}
  </span>
  <span id="slotted-content">
    <slot></slot>
  </span>
</div>`
}
const CrRadioButtonMixinLit = superClass => {
    class CrRadioButtonMixinLit extends superClass {
        static get properties() {
            return {
                checked: {
                    type: Boolean,
                    reflect: true
                },
                disabled: {
                    type: Boolean,
                    reflect: true,
                    notify: true
                },
                focusable: {
                    type: Boolean
                },
                hideLabelText: {
                    type: Boolean,
                    reflect: true
                },
                label: {
                    type: String
                },
                name: {
                    type: String,
                    notify: true,
                    reflect: true
                },
                ariaCheckedString: {
                    type: String
                },
                ariaDisabledString: {
                    type: String
                }
            }
        }
        #checked_accessor_storage = false;
        get checked() {
            return this.#checked_accessor_storage
        }
        set checked(value) {
            this.#checked_accessor_storage = value
        }
        #disabled_accessor_storage = false;
        get disabled() {
            return this.#disabled_accessor_storage
        }
        set disabled(value) {
            this.#disabled_accessor_storage = value
        }
        #focusable_accessor_storage = false;
        get focusable() {
            return this.#focusable_accessor_storage
        }
        set focusable(value) {
            this.#focusable_accessor_storage = value
        }
        #hideLabelText_accessor_storage = false;
        get hideLabelText() {
            return this.#hideLabelText_accessor_storage
        }
        set hideLabelText(value) {
            this.#hideLabelText_accessor_storage = value
        }
        #label_accessor_storage = "";
        get label() {
            return this.#label_accessor_storage
        }
        set label(value) {
            this.#label_accessor_storage = value
        }
        #name_accessor_storage;
        get name() {
            return this.#name_accessor_storage
        }
        set name(value) {
            this.#name_accessor_storage = value
        }
        noRipple = false;
        #ariaCheckedString_accessor_storage = "false";
        get ariaCheckedString() {
            return this.#ariaCheckedString_accessor_storage
        }
        set ariaCheckedString(value) {
            this.#ariaCheckedString_accessor_storage = value
        }
        #ariaDisabledString_accessor_storage = "false";
        get ariaDisabledString() {
            return this.#ariaDisabledString_accessor_storage
        }
        set ariaDisabledString(value) {
            this.#ariaDisabledString_accessor_storage = value
        }
        connectedCallback() {
            super.connectedCallback();
            if (!this.noRipple) {
                this.addEventListener("blur", this.hideRipple_.bind(this));
                this.addEventListener("up", this.hideRipple_.bind(this))
            }
        }
        updated(changedProperties) {
            super.updated(changedProperties);
            if (changedProperties.has("focusable")) {
                const links = this.querySelectorAll("a");
                links.forEach((link => {
                    link.tabIndex = this.checked ? 0 : -1
                }
                ))
            }
        }
        getAriaDisabled() {
            return this.disabled ? "true" : "false"
        }
        getAriaChecked() {
            return this.checked ? "true" : "false"
        }
        getButtonTabIndex() {
            return this.focusable ? 0 : -1
        }
        focus() {
            const button = this.shadowRoot.querySelector("#button");
            assert(button);
            button.focus()
        }
        getRipple() {
            assertNotReached()
        }
        hideRipple_() {
            assert(!this.noRipple);
            this.getRipple().clear()
        }
        onInputKeydown(e) {
            if (e.shiftKey && e.key === "Tab") {
                this.focus()
            }
        }
    }
    return CrRadioButtonMixinLit
}
;
const CrRadioButtonElementBase = CrRippleMixin(CrRadioButtonMixinLit(CrLitElement));
class CrRadioButtonElement extends CrRadioButtonElementBase {
    static get is() {
        return "cr-radio-button"
    }
    static get styles() {
        return getCss$G()
    }
    render() {
        return getHtml$z.bind(this)()
    }
    createRipple() {
        this.rippleContainer = this.shadowRoot.querySelector(".disc-wrapper");
        const ripple = super.createRipple();
        ripple.setAttribute("recenters", "");
        ripple.classList.add("circle");
        return ripple
    }
}
customElements.define(CrRadioButtonElement.is, CrRadioButtonElement);
let instance$H = null;
function getCss$F() {
    return instance$H || (instance$H = [...[], css`:host{display:inline-block}:host ::slotted(*){padding:var(--cr-radio-group-item-padding,12px)}:host([disabled]){cursor:initial;pointer-events:none;user-select:none}:host([disabled]) ::slotted(*){opacity:var(--cr-disabled-opacity)}
`])
}
function getHtml$y() {
    return html`<slot></slot>`
}
function isEnabled(radio) {
    return radio.matches(":not([disabled]):not([hidden])") && radio.style.display !== "none" && radio.style.visibility !== "hidden"
}
class CrRadioGroupElement extends CrLitElement {
    static get is() {
        return "cr-radio-group"
    }
    static get styles() {
        return getCss$F()
    }
    render() {
        return getHtml$y.bind(this)()
    }
    static get properties() {
        return {
            disabled: {
                type: Boolean,
                reflect: true
            },
            selected: {
                type: String,
                notify: true
            },
            selectableElements: {
                type: String
            },
            nestedSelectable: {
                type: Boolean
            },
            selectableRegExp_: {
                type: Object
            }
        }
    }
    #disabled_accessor_storage = false;
    get disabled() {
        return this.#disabled_accessor_storage
    }
    set disabled(value) {
        this.#disabled_accessor_storage = value
    }
    #selected_accessor_storage;
    get selected() {
        return this.#selected_accessor_storage
    }
    set selected(value) {
        this.#selected_accessor_storage = value
    }
    #selectableElements_accessor_storage = "cr-radio-button, cr-card-radio-button, controlled-radio-button";
    get selectableElements() {
        return this.#selectableElements_accessor_storage
    }
    set selectableElements(value) {
        this.#selectableElements_accessor_storage = value
    }
    #nestedSelectable_accessor_storage = false;
    get nestedSelectable() {
        return this.#nestedSelectable_accessor_storage
    }
    set nestedSelectable(value) {
        this.#nestedSelectable_accessor_storage = value
    }
    #selectableRegExp__accessor_storage = new RegExp("");
    get selectableRegExp_() {
        return this.#selectableRegExp__accessor_storage
    }
    set selectableRegExp_(value) {
        this.#selectableRegExp__accessor_storage = value
    }
    buttons_ = null;
    buttonEventTracker_ = new EventTracker;
    deltaKeyMap_ = null;
    isRtl_ = false;
    populateBound_ = null;
    connectedCallback() {
        super.connectedCallback();
        this.isRtl_ = this.matches(":host-context([dir=rtl]) cr-radio-group");
        this.deltaKeyMap_ = new Map([["ArrowDown", 1], ["ArrowLeft", this.isRtl_ ? 1 : -1], ["ArrowRight", this.isRtl_ ? -1 : 1], ["ArrowUp", -1], ["PageDown", 1], ["PageUp", -1]]);
        this.populateBound_ = () => this.populate_();
        assert(this.populateBound_);
        this.shadowRoot.querySelector("slot").addEventListener("slotchange", this.populateBound_);
        this.populate_()
    }
    disconnectedCallback() {
        super.disconnectedCallback();
        assert(this.populateBound_);
        this.shadowRoot.querySelector("slot").removeEventListener("slotchange", this.populateBound_);
        this.buttonEventTracker_.removeAll()
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("selectableElements")) {
            const tags = this.selectableElements.split(", ").join("|");
            this.selectableRegExp_ = new RegExp(`^(${tags})$`,"i")
        }
    }
    firstUpdated() {
        this.addEventListener("keydown", (e => this.onKeyDown_(e)));
        this.addEventListener("click", (e => this.onClick_(e)));
        if (!this.hasAttribute("role")) {
            this.setAttribute("role", "radiogroup")
        }
    }
    updated(changedProperties) {
        if (changedProperties.has("nestedSelectable")) {
            this.populate_()
        }
        if (changedProperties.has("disabled") || changedProperties.has("selected")) {
            this.update_()
        }
        this.setAttribute("aria-disabled", `${this.disabled}`);
        super.updated(changedProperties)
    }
    focus() {
        if (this.disabled || !this.buttons_) {
            return
        }
        const radio = this.buttons_.find((radio => this.isButtonEnabledAndSelected_(radio)));
        if (radio) {
            radio.focus()
        }
    }
    onKeyDown_(event) {
        if (this.disabled) {
            return
        }
        if (event.ctrlKey || event.shiftKey || event.metaKey || event.altKey) {
            return
        }
        const targetElement = event.target;
        if (!this.buttons_ || !this.buttons_.includes(targetElement)) {
            return
        }
        if (event.key === " " || event.key === "Enter") {
            event.preventDefault();
            this.select_(targetElement);
            return
        }
        const enabledRadios = this.buttons_.filter(isEnabled);
        if (enabledRadios.length === 0) {
            return
        }
        assert(this.deltaKeyMap_);
        let selectedIndex;
        const max = enabledRadios.length - 1;
        if (event.key === "Home") {
            selectedIndex = 0
        } else if (event.key === "End") {
            selectedIndex = max
        } else if (this.deltaKeyMap_.has(event.key)) {
            const delta = this.deltaKeyMap_.get(event.key);
            const lastSelection = enabledRadios.findIndex((radio => radio.checked));
            selectedIndex = Math.max(0, lastSelection) + delta;
            if (selectedIndex > max) {
                selectedIndex = 0
            } else if (selectedIndex < 0) {
                selectedIndex = max
            }
        } else {
            return
        }
        const radio = enabledRadios[selectedIndex];
        const name = `${radio.name}`;
        if (this.selected !== name) {
            event.preventDefault();
            event.stopPropagation();
            this.selected = name;
            radio.focus()
        }
    }
    onClick_(event) {
        const path = event.composedPath();
        if (path.some((target => /^a$/i.test(target.tagName)))) {
            return
        }
        const target = path.find((n => this.selectableRegExp_.test(n.tagName)));
        if (target && this.buttons_ && this.buttons_.includes(target)) {
            this.select_(target)
        }
    }
    populate_() {
        const elements = this.shadowRoot.querySelector("slot").assignedElements({
            flatten: true
        });
        this.buttons_ = Array.from(elements).flatMap((el => {
            let result = [];
            if (el.matches(this.selectableElements)) {
                result.push(el)
            }
            if (this.nestedSelectable) {
                result = result.concat(Array.from(el.querySelectorAll(this.selectableElements)))
            }
            return result
        }
        ));
        this.buttonEventTracker_.removeAll();
        this.buttons_.forEach((el => {
            this.buttonEventTracker_.add(el, "disabled-changed", ( () => this.populate_()));
            this.buttonEventTracker_.add(el, "name-changed", ( () => this.populate_()))
        }
        ));
        this.update_()
    }
    select_(button) {
        if (!isEnabled(button)) {
            return
        }
        const name = `${button.name}`;
        if (this.selected !== name) {
            this.selected = name
        }
    }
    isButtonEnabledAndSelected_(button) {
        return !this.disabled && button.checked && isEnabled(button)
    }
    update_() {
        if (!this.buttons_) {
            return
        }
        let noneMadeFocusable = true;
        this.buttons_.forEach((radio => {
            radio.checked = this.selected !== undefined && `${radio.name}` === `${this.selected}`;
            const disabled = this.disabled || !isEnabled(radio);
            const canBeFocused = radio.checked && !disabled;
            if (canBeFocused) {
                radio.focusable = true;
                noneMadeFocusable = false
            } else {
                radio.focusable = false
            }
            radio.setAttribute("aria-disabled", `${disabled}`)
        }
        ));
        if (noneMadeFocusable && !this.disabled) {
            const radio = this.buttons_.find(isEnabled);
            if (radio) {
                radio.focusable = true
            }
        }
    }
}
customElements.define(CrRadioGroupElement.is, CrRadioGroupElement);
const sheet = new CSSStyleSheet;
sheet.replaceSync(`html{--iron-icon-height:20px;--iron-icon-width:20px;--viewer-border-color:rgb(94,94,94);--viewer-icon-focus-outline-color:var(--google-grey-500);--viewer-icon-ink-background-color:rgb(143,143,143);--viewer-icon-ink-fill-color:rgb(199,199,199);--viewer-icon-ink-selected-fill-color:rgb(168,199,250);--viewer-icon-ink-selected-background-color:rgba(76,141,246,0.32);--viewer-text-annotation-active-color:rgb(11,87,208);--viewer-text-annotation-border-width:2px;--viewer-text-annotation-handle-size:10px;--viewer-text-annotation-total-padding-inline:10px;--viewer-text-annotation-total-padding-vert:8px;--viewer-text-annotation-offset-x:calc(var(--viewer-text-annotation-border-width) + var(--viewer-text-annotation-total-padding-inline));--viewer-text-annotation-offset-y:calc(var(--viewer-text-annotation-border-width) + var(--viewer-text-annotation-total-padding-vert));--viewer-text-annotation-padding-x:calc(2 * var(--viewer-text-annotation-offset-x));--viewer-text-annotation-padding-y:calc(2 * var(--viewer-text-annotation-offset-y));--viewer-text-annotation-offset-x-rotated:calc(var(--viewer-text-annotation-border-width) + var(--viewer-text-annotation-total-padding-vert));--viewer-text-annotation-offset-y-rotated:calc(var(--viewer-text-annotation-border-width) + var(--viewer-text-annotation-total-padding-inline));--viewer-text-annotation-padding-x-rotated:calc(2 * var(--viewer-text-annotation-offset-x-rotated));--viewer-text-annotation-padding-y-rotated:calc(2 * var(--viewer-text-annotation-offset-y-rotated));--viewer-pdf-toolbar-background-color:rgb(60,60,60);--viewer-side-background-color:rgb(40,41,42);--viewer-text-input-selection-color:rgba(255,255,255,0.3)}`);
document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet];
let instance$G = null;
function getCss$E() {
    return instance$G || (instance$G = [...[], css`cr-icon-button{--cr-icon-button-fill-color:var(--pdf-toolbar-text-color);--cr-icon-button-focus-outline-color:var(--viewer-icon-focus-outline-color);margin:0}cr-icon-button:hover{background:rgba(255,255,255,0.08);border-radius:50%}cr-action-menu,viewer-bookmark{--cr-menu-background-color:var(--google-grey-900);--cr-menu-shadow:rgba(0,0,0,.3) 0 1px 2px 0,rgba(0,0,0,.15) 0 3px 6px 2px;--cr-primary-text-color:var(--google-grey-200);--cr-menu-background-focus-color:var(--google-grey-700);--cr-separator-line:var(--cr-separator-height) solid rgba(255,255,255,.1);--cr-action-menu-disabled-item-color:var(--cr-primary-text-color);--cr-action-menu-disabled-item-opacity:var(--cr-disabled-opacity)}.md-select{--cr-fallback-color-neutral-outline:rgb(117,117,117);--cr-focus-outline-color:var(--viewer-icon-focus-outline-color);--md-select-option-bg-color:var(--google-grey-900-white-4-percent);--md-select-text-color:rgb(227,227,227);background-image:url(chrome://resources/images/dark/arrow_down.svg)}.md-select:hover{background-color:rgba(253,252,251,.10)}`])
}
let instance$F = null;
function getCss$D() {
    return instance$F || (instance$F = [...[getCss$E()], css`cr-icon-button{--cr-icon-button-fill-color:var(--viewer-icon-ink-fill-color);--cr-icon-button-icon-size:var(--selectable-icon-button-icon-size,20px);--cr-icon-button-size:var(--selectable-icon-button-size,32px)}:host([checked]) cr-icon-button{--cr-icon-button-fill-color:var(--viewer-icon-ink-selected-fill-color);background-color:var(--viewer-icon-ink-selected-background-color)}`])
}
function getHtml$x() {
    return html`
<cr-icon-button id="button" role="radio" iron-icon="${this.icon}"
    tabindex="${this.getButtonTabIndex()}"
    aria-checked="${this.getAriaChecked()}"
    aria-disabled="${this.getAriaDisabled()}" aria-label="${this.label}"
    title="${this.label}" @keydown="${this.onInputKeydown}">
</cr-icon-button>`
}
const SelectableIconButtonElementBase = CrRadioButtonMixinLit(CrLitElement);
class SelectableIconButtonElement extends SelectableIconButtonElementBase {
    static get is() {
        return "selectable-icon-button"
    }
    static get styles() {
        return getCss$D()
    }
    render() {
        return getHtml$x.bind(this)()
    }
    static get properties() {
        return {
            icon: {
                type: String
            }
        }
    }
    #icon_accessor_storage = "";
    get icon() {
        return this.#icon_accessor_storage
    }
    set icon(value) {
        this.#icon_accessor_storage = value
    }
    noRipple = true
}
customElements.define(SelectableIconButtonElement.is, SelectableIconButtonElement);
function sanitizeInnerHtmlInternal(rawString, opts) {
    opts = opts || {};
    const html = parseHtmlSubset(`<b>${rawString}</b>`, opts.tags, opts.attrs).firstElementChild;
    return html.innerHTML
}
let sanitizedPolicy = null;
function sanitizeInnerHtml(rawString, opts) {
    assert(window.trustedTypes);
    if (sanitizedPolicy === null) {
        sanitizedPolicy = window.trustedTypes.createPolicy("sanitize-inner-html", {
            createHTML: sanitizeInnerHtmlInternal,
            createScript: () => assertNotReached(),
            createScriptURL: () => assertNotReached()
        })
    }
    return sanitizedPolicy.createHTML(rawString, opts)
}
const allowAttribute = (_node, _value) => true;
const allowedAttributes = new Map([["href", (node, value) => node.tagName === "A" && (value.startsWith("chrome://") || value.startsWith("https://") || value === "#")], ["target", (node, value) => node.tagName === "A" && value === "_blank"]]);
const allowedOptionalAttributes = new Map([["class", allowAttribute], ["id", allowAttribute], ["is", (_node, value) => value === "action-link" || value === ""], ["role", (_node, value) => value === "link"], ["src", (node, value) => node.tagName === "IMG" && value.startsWith("chrome://")], ["tabindex", allowAttribute], ["aria-description", allowAttribute], ["aria-hidden", allowAttribute], ["aria-label", allowAttribute], ["aria-labelledby", allowAttribute]]);
const allowedTags = new Set(["A", "B", "I", "BR", "DIV", "EM", "KBD", "P", "PRE", "SPAN", "STRONG"]);
const allowedOptionalTags = new Set(["IMG", "LI", "UL"]);
let unsanitizedPolicy;
function mergeTags(optTags) {
    const clone = new Set(allowedTags);
    optTags.forEach((str => {
        const tag = str.toUpperCase();
        if (allowedOptionalTags.has(tag)) {
            clone.add(tag)
        }
    }
    ));
    return clone
}
function mergeAttrs(optAttrs) {
    const clone = new Map(allowedAttributes);
    optAttrs.forEach((key => {
        if (allowedOptionalAttributes.has(key)) {
            clone.set(key, allowedOptionalAttributes.get(key))
        }
    }
    ));
    return clone
}
function walk(n, f) {
    f(n);
    for (let i = 0; i < n.childNodes.length; i++) {
        walk(n.childNodes[i], f)
    }
}
function assertElement(tags, node) {
    if (!tags.has(node.tagName)) {
        throw Error(node.tagName + " is not supported")
    }
}
function assertAttribute(attrs, attrNode, node) {
    const n = attrNode.nodeName;
    const v = attrNode.nodeValue || "";
    if (!attrs.has(n) || !attrs.get(n)(node, v)) {
        throw Error(node.tagName + "[" + n + '="' + v + '"] is not supported')
    }
}
function parseHtmlSubset(s, extraTags, extraAttrs) {
    const tags = extraTags ? mergeTags(extraTags) : allowedTags;
    const attrs = extraAttrs ? mergeAttrs(extraAttrs) : allowedAttributes;
    const doc = document.implementation.createHTMLDocument("");
    const r = doc.createRange();
    r.selectNode(doc.body);
    if (window.trustedTypes) {
        if (!unsanitizedPolicy) {
            unsanitizedPolicy = window.trustedTypes.createPolicy("parse-html-subset", {
                createHTML: untrustedHTML => untrustedHTML,
                createScript: () => assertNotReached(),
                createScriptURL: () => assertNotReached()
            })
        }
        s = unsanitizedPolicy.createHTML(s)
    }
    const df = r.createContextualFragment(s);
    walk(df, (function(node) {
        switch (node.nodeType) {
        case Node.ELEMENT_NODE:
            assertElement(tags, node);
            const nodeAttrs = node.attributes;
            for (let i = 0; i < nodeAttrs.length; ++i) {
                assertAttribute(attrs, nodeAttrs[i], node)
            }
            break;
        case Node.COMMENT_NODE:
        case Node.DOCUMENT_FRAGMENT_NODE:
        case Node.TEXT_NODE:
            break;
        default:
            throw Error("Node type " + node.nodeType + " is not supported")
        }
    }
    ));
    return df
}
const I18nMixinLit = superClass => {
    class I18nMixinLit extends superClass {
        i18nRaw_(id, ...varArgs) {
            return varArgs.length === 0 ? loadTimeData.getString(id) : loadTimeData.getStringF(id, ...varArgs)
        }
        i18n(id, ...varArgs) {
            const rawString = this.i18nRaw_(id, ...varArgs);
            return parseHtmlSubset(`<b>${rawString}</b>`).firstChild.textContent
        }
        i18nAdvanced(id, opts) {
            opts = opts || {};
            const rawString = this.i18nRaw_(id, ...opts.substitutions || []);
            return sanitizeInnerHtml(rawString, opts)
        }
        i18nDynamic(_locale, id, ...varArgs) {
            return this.i18n(id, ...varArgs)
        }
        i18nRecursive(locale, id, ...varArgs) {
            let args = varArgs;
            if (args.length > 0) {
                args = args.map((str => this.i18nExists(str) ? loadTimeData.getString(str) : str))
            }
            return this.i18nDynamic(locale, id, ...args)
        }
        i18nExists(id) {
            return loadTimeData.valueExists(id)
        }
    }
    return I18nMixinLit
}
;
let instance$E = null;
function getCss$C() {
    return instance$E || (instance$E = [...[getCss$E()], css`:host{display:inline-block}cr-radio-group{--cr-radio-group-item-padding:6px;display:flex;justify-content:center}selectable-icon-button{--selectable-icon-button-size:36px;--selectable-icon-button-icon-size:24px}`])
}
function getHtml$w() {
    return html`<!--_html_template_start_-->
<cr-radio-group selectable-elements="selectable-icon-button"
    .selected="${this.currentSizeString_()}" aria-label="Size"
    @selected-changed="${this.onSelectedChanged_}">
  ${this.getCurrentBrushSizes_().map((item => html`
    <selectable-icon-button icon="pdf-ink:${item.icon}" name="${item.size}"
        label="${this.i18n(item.label)}">
    </selectable-icon-button>
  `))}
</cr-radio-group>
<!--_html_template_end_-->`
}
const PEN_SIZES = [{
    icon: "pen-size-1",
    label: "ink2BrushSizeExtraThin",
    size: 1
}, {
    icon: "pen-size-2",
    label: "ink2BrushSizeThin",
    size: 2
}, {
    icon: "pen-size-3",
    label: "ink2BrushSizeMedium",
    size: 3
}, {
    icon: "pen-size-4",
    label: "ink2BrushSizeThick",
    size: 6
}, {
    icon: "pen-size-5",
    label: "ink2BrushSizeExtraThick",
    size: 8
}];
const HIGHLIGHTER_SIZES = [{
    icon: "highlighter-size-1",
    label: "ink2BrushSizeExtraThin",
    size: 4
}, {
    icon: "highlighter-size-2",
    label: "ink2BrushSizeThin",
    size: 6
}, {
    icon: "highlighter-size-3",
    label: "ink2BrushSizeMedium",
    size: 8
}, {
    icon: "highlighter-size-4",
    label: "ink2BrushSizeThick",
    size: 12
}, {
    icon: "highlighter-size-5",
    label: "ink2BrushSizeExtraThick",
    size: 16
}];
const InkSizeSelectorElementBase = I18nMixinLit(CrLitElement);
class InkSizeSelectorElement extends InkSizeSelectorElementBase {
    static get is() {
        return "ink-size-selector"
    }
    static get styles() {
        return getCss$C()
    }
    render() {
        return getHtml$w.bind(this)()
    }
    static get properties() {
        return {
            currentSize: {
                notify: true,
                type: Number
            },
            currentType: {
                type: String
            }
        }
    }
    focus() {
        const selectedButton = this.shadowRoot.querySelector("selectable-icon-button[checked]");
        assert(selectedButton);
        selectedButton.focus()
    }
    #currentSize_accessor_storage = 0;
    get currentSize() {
        return this.#currentSize_accessor_storage
    }
    set currentSize(value) {
        this.#currentSize_accessor_storage = value
    }
    #currentType_accessor_storage = AnnotationBrushType.PEN;
    get currentType() {
        return this.#currentType_accessor_storage
    }
    set currentType(value) {
        this.#currentType_accessor_storage = value
    }
    currentSizeString_() {
        return this.currentSize.toString()
    }
    onSelectedChanged_(e) {
        this.currentSize = Number(e.detail.value)
    }
    getCurrentBrushSizes_() {
        assert(this.currentType !== AnnotationBrushType.ERASER);
        return this.currentType === AnnotationBrushType.HIGHLIGHTER ? HIGHLIGHTER_SIZES : PEN_SIZES
    }
}
customElements.define(InkSizeSelectorElement.is, InkSizeSelectorElement);
const HIGHLIGHTER_COLORS = [{
    label: "ink2BrushColorLightRed",
    color: "#f28b82",
    blended: true
}, {
    label: "ink2BrushColorLightYellow",
    color: "#fdd663",
    blended: true
}, {
    label: "annotationColorLightGreen",
    color: "#34a853",
    blended: true
}, {
    label: "annotationColorLightBlue",
    color: "#4285f4",
    blended: true
}, {
    label: "annotationColorLightOrange",
    color: "#ffae80",
    blended: true
}, {
    label: "annotationColorRed",
    color: "#d93025",
    blended: true
}, {
    label: "annotationColorYellow",
    color: "#ddf300",
    blended: true
}, {
    label: "annotationColorGreen",
    color: "#25e387",
    blended: true
}, {
    label: "annotationColorBlue",
    color: "#5379ff",
    blended: true
}, {
    label: "annotationColorOrange",
    color: "#ff630c",
    blended: true
}];
const PEN_COLORS = [{
    label: "annotationColorBlack",
    color: "#000000",
    blended: false
}, {
    label: "ink2BrushColorDarkGrey2",
    color: "#5f6368",
    blended: false
}, {
    label: "ink2BrushColorDarkGrey1",
    color: "#9aa0a6",
    blended: false
}, {
    label: "annotationColorLightGrey",
    color: "#dadce0",
    blended: false
}, {
    label: "annotationColorWhite",
    color: "#ffffff",
    blended: false
}, {
    label: "ink2BrushColorRed1",
    color: "#f28b82",
    blended: false
}, {
    label: "ink2BrushColorYellow1",
    color: "#fdd663",
    blended: false
}, {
    label: "ink2BrushColorGreen1",
    color: "#81c995",
    blended: false
}, {
    label: "ink2BrushColorBlue1",
    color: "#8ab4f8",
    blended: false
}, {
    label: "ink2BrushColorTan1",
    color: "#eec9ae",
    blended: false
}, {
    label: "ink2BrushColorRed2",
    color: "#ea4335",
    blended: false
}, {
    label: "ink2BrushColorYellow2",
    color: "#fbbc04",
    blended: false
}, {
    label: "ink2BrushColorGreen2",
    color: "#34a853",
    blended: false
}, {
    label: "ink2BrushColorBlue2",
    color: "#4285f4",
    blended: false
}, {
    label: "ink2BrushColorTan2",
    color: "#e2a185",
    blended: false
}, {
    label: "ink2BrushColorRed3",
    color: "#c5221f",
    blended: false
}, {
    label: "ink2BrushColorYellow3",
    color: "#f29900",
    blended: false
}, {
    label: "ink2BrushColorGreen3",
    color: "#188038",
    blended: false
}, {
    label: "ink2BrushColorBlue3",
    color: "#1967d2",
    blended: false
}, {
    label: "ink2BrushColorTan3",
    color: "#885945",
    blended: false
}];
const InkAnnotationBrushMixin = superClass => {
    class InkAnnotationBrushMixin extends superClass {
        static get properties() {
            return {
                currentColor: {
                    type: Object
                },
                currentSize: {
                    type: Number
                },
                currentType: {
                    type: String
                }
            }
        }
        tracker_ = new EventTracker;
        #currentColor_accessor_storage = {
            r: 0,
            g: 0,
            b: 0
        };
        get currentColor() {
            return this.#currentColor_accessor_storage
        }
        set currentColor(value) {
            this.#currentColor_accessor_storage = value
        }
        #currentSize_accessor_storage = PEN_SIZES[0].size;
        get currentSize() {
            return this.#currentSize_accessor_storage
        }
        set currentSize(value) {
            this.#currentSize_accessor_storage = value
        }
        #currentType_accessor_storage = AnnotationBrushType.PEN;
        get currentType() {
            return this.#currentType_accessor_storage
        }
        set currentType(value) {
            this.#currentType_accessor_storage = value
        }
        constructor(..._args) {
            super();
            if (Ink2Manager.getInstance().isInitializationComplete()) {
                this.onBrushChanged_(Ink2Manager.getInstance().getCurrentBrush())
            }
        }
        connectedCallback() {
            super.connectedCallback();
            this.tracker_.add(Ink2Manager.getInstance(), "brush-changed", (e => this.onBrushChanged_(e.detail)))
        }
        disconnectedCallback() {
            super.disconnectedCallback();
            this.tracker_.removeAll()
        }
        availableBrushColors() {
            assert(this.currentType !== AnnotationBrushType.ERASER);
            return this.currentType === AnnotationBrushType.PEN ? PEN_COLORS : HIGHLIGHTER_COLORS
        }
        onCurrentColorChanged(e) {
            const newColor = e.detail.value;
            if (newColor.r !== this.currentColor.r || newColor.b !== this.currentColor.b || newColor.g !== this.currentColor.g) {
                Ink2Manager.getInstance().setBrushColor(newColor)
            }
        }
        onCurrentSizeChanged(e) {
            if (e.detail.value !== this.currentSize) {
                Ink2Manager.getInstance().setBrushSize(e.detail.value)
            }
        }
        onCurrentTypeChanged(e) {
            if (e.detail.value !== this.currentType) {
                Ink2Manager.getInstance().setBrushType(e.detail.value)
            }
        }
        onBrushChanged_(brush) {
            this.currentType = brush.type;
            if (brush.size !== undefined) {
                this.currentSize = brush.size
            }
            if (brush.color !== undefined) {
                this.currentColor = brush.color
            }
        }
    }
    return InkAnnotationBrushMixin
}
;
const TEXT_SIZES = [6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 40, 48, 64, 72, 100];
const TEXT_COLORS = [{
    label: "annotationColorBlack",
    color: "#000000",
    blended: false
}, {
    label: "ink2BrushColorDarkGrey2",
    color: "#5f6368",
    blended: false
}, {
    label: "ink2BrushColorDarkGrey1",
    color: "#9aa0a6",
    blended: false
}, {
    label: "annotationColorLightGrey",
    color: "#dadce0",
    blended: false
}, {
    label: "annotationColorWhite",
    color: "#ffffff",
    blended: false
}, {
    label: "ink2BrushColorRed1",
    color: "#f28b82",
    blended: false
}, {
    label: "ink2BrushColorYellow1",
    color: "#fdd663",
    blended: false
}, {
    label: "ink2BrushColorGreen1",
    color: "#81c995",
    blended: false
}, {
    label: "ink2TextColorCyan1",
    color: "#78d9ec",
    blended: false
}, {
    label: "ink2BrushColorBlue1",
    color: "#8ab4f8",
    blended: false
}, {
    label: "ink2BrushColorRed2",
    color: "#e94235",
    blended: false
}, {
    label: "ink2BrushColorYellow2",
    color: "#fbbc04",
    blended: false
}, {
    label: "ink2BrushColorGreen2",
    color: "#34a853",
    blended: false
}, {
    label: "ink2TextColorCyan2",
    color: "#24c1e0",
    blended: false
}, {
    label: "ink2BrushColorBlue2",
    color: "#4285f4",
    blended: false
}, {
    label: "ink2BrushColorRed3",
    color: "#c5221f",
    blended: false
}, {
    label: "ink2BrushColorYellow3",
    color: "#d56e0c",
    blended: false
}, {
    label: "ink2BrushColorGreen3",
    color: "#188038",
    blended: false
}, {
    label: "ink2TextColorCyan3",
    color: "#12a4af",
    blended: false
}, {
    label: "ink2BrushColorBlue3",
    color: "#1967d2",
    blended: false
}];
const InkAnnotationTextMixin = superClass => {
    class InkAnnotationTextMixin extends superClass {
        static get properties() {
            return {
                colors: {
                    type: Array
                },
                currentColor: {
                    type: Object
                },
                currentSize: {
                    type: Number
                },
                currentTypeface: {
                    type: String
                },
                fontNames: {
                    type: Array
                },
                sizes: {
                    type: Array
                }
            }
        }
        #currentColor_accessor_storage = hexToColor(TEXT_COLORS[0].color);
        get currentColor() {
            return this.#currentColor_accessor_storage
        }
        set currentColor(value) {
            this.#currentColor_accessor_storage = value
        }
        #currentSize_accessor_storage = TEXT_SIZES[3];
        get currentSize() {
            return this.#currentSize_accessor_storage
        }
        set currentSize(value) {
            this.#currentSize_accessor_storage = value
        }
        #currentTypeface_accessor_storage = TextTypeface.SANS_SERIF;
        get currentTypeface() {
            return this.#currentTypeface_accessor_storage
        }
        set currentTypeface(value) {
            this.#currentTypeface_accessor_storage = value
        }
        #colors_accessor_storage = TEXT_COLORS;
        get colors() {
            return this.#colors_accessor_storage
        }
        set colors(value) {
            this.#colors_accessor_storage = value
        }
        #fontNames_accessor_storage = [TextTypeface.SANS_SERIF, TextTypeface.SERIF, TextTypeface.MONOSPACE];
        get fontNames() {
            return this.#fontNames_accessor_storage
        }
        set fontNames(value) {
            this.#fontNames_accessor_storage = value
        }
        #sizes_accessor_storage = TEXT_SIZES;
        get sizes() {
            return this.#sizes_accessor_storage
        }
        set sizes(value) {
            this.#sizes_accessor_storage = value
        }
        firstUpdated(changedProperties) {
            super.firstUpdated(changedProperties);
            const typefaceSelect = this.shadowRoot.querySelector("#typefaceSelect");
            assert(typefaceSelect);
            typefaceSelect.value = this.currentTypeface;
            const sizeSelect = this.shadowRoot.querySelector("#sizeSelect");
            assert(sizeSelect);
            sizeSelect.value = this.currentSize.toString()
        }
        getLabelForTypeface(typeface) {
            switch (typeface) {
            case TextTypeface.SANS_SERIF:
                return "ink2TextFontSansSerif";
            case TextTypeface.SERIF:
                return "ink2TextFontSerif";
            case TextTypeface.MONOSPACE:
                return "ink2TextFontMonospace";
            default:
                assertNotReachedCase()
            }
        }
        onTypefaceSelected(e) {
            const newValue = e.target.value;
            Ink2Manager.getInstance().setTextTypeface(newValue)
        }
        onSizeSelected(e) {
            const newValue = Number(e.target.value);
            Ink2Manager.getInstance().setTextSize(newValue)
        }
        onCurrentColorChanged(e) {
            const newColor = e.detail.value;
            if (!colorsEqual(newColor, this.currentColor)) {
                Ink2Manager.getInstance().setTextColor(newColor)
            }
        }
        onTextAttributesChanged(attributes) {
            this.currentColor = attributes.color;
            this.currentTypeface = attributes.typeface;
            this.currentSize = attributes.size
        }
    }
    return InkAnnotationTextMixin
}
;
let instance$D = null;
function getCss$B() {
    return instance$D || (instance$D = [...[getCss$E()], css`:host,cr-radio-group{--cr-radio-group-item-padding:0;display:flex;gap:var(--ink-brush-button-gap,16px);justify-content:center}selectable-icon-button{--selectable-icon-button-size:var(--ink-brush-button-size,48px)}`])
}
function getHtml$v() {
    return html`<!--_html_template_start_-->
<cr-radio-group selectable-elements="selectable-icon-button"
    .selected="${this.currentType}" aria-label="Tool"
    @selected-changed="${this.onSelectedChanged_}">
  ${BRUSH_TYPES.map((brush => html`
    <selectable-icon-button id="${brush}" icon="${this.getIcon_(brush)}"
        name="${brush}" label="${this.getLabel_(brush)}">
    </selectable-icon-button>
  `))}
</cr-radio-group>
<!--_html_template_end_-->`
}
const BRUSH_TYPES = [AnnotationBrushType.PEN, AnnotationBrushType.HIGHLIGHTER, AnnotationBrushType.ERASER];
class InkBrushSelectorElement extends CrLitElement {
    static get is() {
        return "ink-brush-selector"
    }
    static get styles() {
        return getCss$B()
    }
    render() {
        return getHtml$v.bind(this)()
    }
    static get properties() {
        return {
            currentType: {
                notify: true,
                type: String
            }
        }
    }
    #currentType_accessor_storage = AnnotationBrushType.PEN;
    get currentType() {
        return this.#currentType_accessor_storage
    }
    set currentType(value) {
        this.#currentType_accessor_storage = value
    }
    onSelectedChanged_(e) {
        const newType = e.detail.value;
        if (newType === this.currentType) {
            return
        }
        this.currentType = newType;
        switch (newType) {
        case AnnotationBrushType.ERASER:
            record(UserAction.SELECT_INK2_BRUSH_ERASER);
            break;
        case AnnotationBrushType.HIGHLIGHTER:
            record(UserAction.SELECT_INK2_BRUSH_HIGHLIGHTER);
            break;
        case AnnotationBrushType.PEN:
            record(UserAction.SELECT_INK2_BRUSH_PEN);
            break;
        default:
            assertNotReachedCase()
        }
    }
    getIcon_(type) {
        const isCurrentType = type === this.currentType;
        switch (type) {
        case AnnotationBrushType.ERASER:
            return isCurrentType ? "pdf-ink:ink-eraser-filled" : "pdf-ink:ink-eraser";
        case AnnotationBrushType.HIGHLIGHTER:
            return isCurrentType ? "pdf-ink:ink-highlighter-filled" : "pdf-ink:ink-highlighter";
        case AnnotationBrushType.PEN:
            return isCurrentType ? "pdf-ink:ink-pen-filled" : "pdf-ink:ink-pen";
        default:
            assertNotReachedCase()
        }
    }
    getLabel_(type) {
        switch (type) {
        case AnnotationBrushType.ERASER:
            return loadTimeData.getString("annotationEraser");
        case AnnotationBrushType.HIGHLIGHTER:
            return loadTimeData.getString("annotationHighlighter");
        case AnnotationBrushType.PEN:
            return loadTimeData.getString("annotationPen");
        default:
            assertNotReachedCase()
        }
    }
}
customElements.define(InkBrushSelectorElement.is, InkBrushSelectorElement);
let instance$C = null;
function getCss$A() {
    return instance$C || (instance$C = [...[], css`:host{--cr-grid-gap:0px;--cr-column-width:auto;--cr-grid-width:fit-content}#grid{display:grid;grid-gap:var(--cr-grid-gap);grid-template-columns:repeat(var(--cr-grid-columns),var(--cr-column-width));width:var(--cr-grid-width)}::slotted(*){align-self:center;justify-self:center}`])
}
function getHtml$u() {
    return html`
<div id="grid" @keydown="${this.onKeydown_}">
  <slot id="items"></slot>
</div>`
}
class CrGridElement extends CrLitElement {
    static get is() {
        return "cr-grid"
    }
    static get styles() {
        return getCss$A()
    }
    render() {
        return getHtml$u.bind(this)()
    }
    static get properties() {
        return {
            columns: {
                type: Number
            },
            disableArrowNavigation: {
                type: Boolean
            },
            focusSelector: {
                type: String
            },
            ignoreModifiedKeyEvents: {
                type: Boolean
            }
        }
    }
    #columns_accessor_storage = 1;
    get columns() {
        return this.#columns_accessor_storage
    }
    set columns(value) {
        this.#columns_accessor_storage = value
    }
    #disableArrowNavigation_accessor_storage = false;
    get disableArrowNavigation() {
        return this.#disableArrowNavigation_accessor_storage
    }
    set disableArrowNavigation(value) {
        this.#disableArrowNavigation_accessor_storage = value
    }
    #focusSelector_accessor_storage;
    get focusSelector() {
        return this.#focusSelector_accessor_storage
    }
    set focusSelector(value) {
        this.#focusSelector_accessor_storage = value
    }
    #ignoreModifiedKeyEvents_accessor_storage = false;
    get ignoreModifiedKeyEvents() {
        return this.#ignoreModifiedKeyEvents_accessor_storage
    }
    set ignoreModifiedKeyEvents(value) {
        this.#ignoreModifiedKeyEvents_accessor_storage = value
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("columns")) {
            this.style.setProperty("--cr-grid-columns", String(this.columns))
        }
    }
    getSlottedParent_(element) {
        let parent = element;
        while (parent.assignedSlot !== this.$.items && parent.parentElement !== null) {
            parent = parent.parentElement
        }
        assert(parent);
        return parent
    }
    onKeydown_(e) {
        if (e.key === " " || e.key === "Enter" && !(isMac && e.ctrlKey)) {
            e.preventDefault();
            e.stopPropagation();
            e.target.click();
            return
        }
        if (this.disableArrowNavigation || !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(e.key)) {
            return
        }
        const arrowKey = e.key;
        const items = this.$.items.assignedElements().filter((el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)));
        const currentIndex = items.indexOf(this.getSlottedParent_(e.target));
        const isRtl = window.getComputedStyle(this)["direction"] === "rtl";
        const bottomRowColumns = items.length % this.columns;
        const direction = ["ArrowRight", "ArrowDown"].includes(arrowKey) ? 1 : -1;
        const inEdgeRow = direction === 1 ? currentIndex >= items.length - bottomRowColumns : currentIndex < this.columns;
        let delta = 0;
        switch (arrowKey) {
        case "ArrowLeft":
        case "ArrowRight":
            if (this.ignoreModifiedKeyEvents && hasKeyModifiers(e)) {
                return
            }
            delta = direction * (isRtl ? -1 : 1);
            break;
        case "ArrowUp":
        case "ArrowDown":
            delta = direction * (inEdgeRow ? bottomRowColumns : this.columns);
            break;
        default:
            assertNotReachedCase()
        }
        if (arrowKey === "ArrowUp" && inEdgeRow && currentIndex >= bottomRowColumns) {
            delta -= this.columns
        } else if (arrowKey === "ArrowDown" && !inEdgeRow && currentIndex + delta >= items.length) {
            delta += bottomRowColumns
        }
        e.preventDefault();
        const newIndex = (items.length + currentIndex + delta) % items.length;
        const item = items[newIndex];
        const toFocus = this.focusSelector ? item.querySelector(this.focusSelector) : item;
        assert(toFocus);
        toFocus.focus();
        this.fire("cr-grid-focus-changed", toFocus)
    }
}
customElements.define(CrGridElement.is, CrGridElement);
let instance$B = null;
function getCss$z() {
    return instance$B || (instance$B = [...[getCss$E()], css`:host{display:inline-block}cr-grid{justify-content:center}.color-item{align-items:center;cursor:pointer;display:flex;height:48px;justify-content:center;width:48px}.color-chip{appearance:none;background:var(--item-color,magenta);border:1px solid var(--viewer-icon-ink-background-color);border-radius:50%;cursor:pointer;margin:0;height:24px;width:24px}.color-chip.blended{background:color-mix(in srgb,var(--item-color) 40%,white)}.color-chip[checked]{height:36px;width:36px}.color-chip:focus-visible:focus{outline:var(--viewer-icon-focus-outline-color) solid 2px;outline-offset:2px}`])
}
function getHtml$t() {
    return html`<!--_html_template_start_-->
<cr-grid role="radiogroup" columns="5" focus-selector=".color-chip"
    aria-label="${this.label}"
    @cr-grid-focus-changed="${this.onCrGridFocusChanged_}">
  ${this.colors.map((item => html`
    <label class="color-item">
      <input type="radio" class="color-chip ${this.getBlendedClass_(item)}"
          name="color" .value="${item.color}"
          .style="--item-color: ${item.color}"
          aria-label="${this.i18n(item.label)}"
          tabindex="${this.getTabIndex_(item.color)}"
          title="${this.i18n(item.label)}" @click="${this.onColorClick_}"
          ?checked="${this.isCurrentColor_(item.color)}">
    </label>
  `))}
</cr-grid>
<!--_html_template_end_-->`
}
const InkColorSelectorElementBase = I18nMixinLit(CrLitElement);
class InkColorSelectorElement extends InkColorSelectorElementBase {
    static get is() {
        return "ink-color-selector"
    }
    static get styles() {
        return getCss$z()
    }
    render() {
        return getHtml$t.bind(this)()
    }
    static get properties() {
        return {
            colors: {
                type: Array
            },
            currentColor: {
                type: Object
            },
            label: {
                type: String
            }
        }
    }
    #colors_accessor_storage = [];
    get colors() {
        return this.#colors_accessor_storage
    }
    set colors(value) {
        this.#colors_accessor_storage = value
    }
    #currentColor_accessor_storage = {
        r: 0,
        g: 0,
        b: 0
    };
    get currentColor() {
        return this.#currentColor_accessor_storage
    }
    set currentColor(value) {
        this.#currentColor_accessor_storage = value
    }
    #label_accessor_storage = "";
    get label() {
        return this.#label_accessor_storage
    }
    set label(value) {
        this.#label_accessor_storage = value
    }
    onColorClick_(e) {
        this.setBrushColor_(e.currentTarget)
    }
    onCrGridFocusChanged_(e) {
        this.setBrushColor_(e.detail)
    }
    focus() {
        const selectedButton = this.shadowRoot.querySelector("input[checked]");
        assert(selectedButton);
        selectedButton.focus()
    }
    getTabIndex_(color) {
        return this.isCurrentColor_(color) ? 0 : -1
    }
    isCurrentColor_(hex) {
        return colorsEqual(this.currentColor, hexToColor(hex))
    }
    getBlendedClass_(item) {
        return item.blended ? "blended" : ""
    }
    setBrushColor_(colorButton) {
        const hex = colorButton.value;
        assert(hex);
        const newColor = hexToColor(hex);
        if (colorsEqual(this.currentColor, newColor)) {
            return
        }
        this.currentColor = newColor;
        this.fire("current-color-changed", {
            value: newColor
        })
    }
}
customElements.define(InkColorSelectorElement.is, InkColorSelectorElement);
class PdfViewerPrivateProxyImpl {
    getTextInfo(textarea, knownFontIds) {
        return chrome.pdfViewerPrivate.getTextInfo(textarea, knownFontIds)
    }
    onSaveToDriveProgress = chrome.pdfViewerPrivate.onSaveToDriveProgress;
    saveToDrive(saveRequestType) {
        chrome.pdfViewerPrivate.saveToDrive(saveRequestType)
    }
    glicSummarize() {
        chrome.pdfViewerPrivate.glicSummarize()
    }
    setPdfDocumentTitle(title) {
        chrome.pdfViewerPrivate.setPdfDocumentTitle(title)
    }
    static getInstance() {
        return instance$A || (instance$A = new PdfViewerPrivateProxyImpl)
    }
    static setInstance(obj) {
        instance$A = obj
    }
}
let instance$A = null;
let instance$z = null;
function getCss$y() {
    return instance$z || (instance$z = [...[getCss$J()], css`:host{--border-padding:calc(var(--viewer-text-annotation-handle-size) / 2);--handle-offset:calc(var(--viewer-text-annotation-border-width) / 2 + var(--border-padding));--primary-color:var(--viewer-text-annotation-active-color);--textarea-padding-inline:calc(var(--viewer-text-annotation-total-padding-inline) - var(--border-padding));--textarea-padding-vert:calc(var(--viewer-text-annotation-total-padding-vert) - var(--border-padding));--offset-x:calc(var(--viewer-text-annotation-offset-x) + var(--border-padding));--offset-y:calc(var(--viewer-text-annotation-offset-y) + var(--border-padding));--textbox-location-x:0;--textbox-location-y:0;cursor:move;top:calc(var(--textbox-location-y) - var(--offset-y));left:calc(var(--textbox-location-x) - var(--offset-x));padding:var(--border-padding);position:absolute;z-index:1}:host([text-rotations_='1']),:host([text-rotations_='3']){--textarea-padding-inline:calc(var(--viewer-text-annotation-total-padding-vert) - var(--border-padding));--textarea-padding-vert:calc(var(--viewer-text-annotation-total-padding-inline) - var(--border-padding));--offset-x:calc(var(--viewer-text-annotation-offset-x-rotated) + var(--border-padding));--offset-y:calc(var(--viewer-text-annotation-offset-y-rotated) + var(--border-padding))}.handle{background-color:var(--primary-color);border:1px solid white;border-radius:50%;height:var(--viewer-text-annotation-handle-size);position:absolute;transform:translate(-50%,-50%);user-select:none;width:var(--viewer-text-annotation-handle-size)}.handle.top{top:var(--handle-offset)}.handle.left{left:var(--handle-offset)}.handle.right{left:calc(100% - var(--handle-offset))}.handle.bottom{top:calc(100% - var(--handle-offset))}.handle.left.center,.handle.right.center{top:50%}.handle.top.center,.handle.bottom.center{left:50%}.handle.left,.handle.right{cursor:ew-resize}.handle.top,.handle.bottom{cursor:ns-resize}.handle.top.right,.handle.bottom.left{cursor:nesw-resize}.handle.top.left,.handle.bottom.right{cursor:nwse-resize}.textbox-wrapper{flex:1;overflow:hidden;padding:var(--border-padding);border:var(--viewer-text-annotation-border-width) solid var(--primary-color);cursor:move;user-select:none}textarea{background:none;border:none;display:block;outline:none;overflow:hidden;padding:var(--textarea-padding-vert) var(--textarea-padding-inline);resize:none}:host([text-rotations_='1']) textarea{writing-mode:vertical-rl}:host([text-rotations_='2']) textarea{transform:rotate(180deg)}:host([text-rotations_='3']) textarea{writing-mode:sideways-lr}`])
}
function getHtml$s() {
    return html`<!--_html_template_start_-->
<div class="textbox-wrapper">
  <textarea id="textbox" .value="${this.textValue_}" rows="1"
      @input="${this.onTextValueInput_}">
  </textarea>
  <div class="handle top left"></div>
  <div class="handle top center"></div>
  <div class="handle top right"></div>
  <div class="handle left center"></div>
  <div class="handle right center"></div>
  <div class="handle bottom left"></div>
  <div class="handle bottom center"></div>
  <div class="handle bottom right"></div>
</div>
<!--_html_template_end_-->`
}
const InkTextObserverMixin = superClass => {
    class InkTextObserverMixin extends superClass {
        tracker_ = new EventTracker;
        firstUpdated() {
            this.onTextAttributesChanged(Ink2Manager.getInstance().getCurrentTextAttributes())
        }
        connectedCallback() {
            super.connectedCallback();
            this.tracker_.add(Ink2Manager.getInstance(), "attributes-changed", (e => this.onTextAttributesChanged(e.detail)))
        }
        disconnectedCallback() {
            super.disconnectedCallback();
            this.tracker_.removeAll()
        }
        onTextAttributesChanged(_attributes) {
            assertNotReached()
        }
    }
    return InkTextObserverMixin
}
;
var TextBoxState;
(function(TextBoxState) {
    TextBoxState[TextBoxState["INACTIVE"] = 0] = "INACTIVE";
    TextBoxState[TextBoxState["NEW"] = 1] = "NEW";
    TextBoxState[TextBoxState["EDITED"] = 2] = "EDITED"
}
)(TextBoxState || (TextBoxState = {}));
const KEYBOARD_RESIZE_STEP_PX = 10;
function getStyleForTypeface(typeface) {
    switch (typeface) {
    case TextTypeface.SANS_SERIF:
        return "Arial, sans-serif";
    case TextTypeface.SERIF:
        return "Times, serif";
    case TextTypeface.MONOSPACE:
        return '"Courier New", monospace';
    default:
        assertNotReachedCase()
    }
}
function isArrowKey(key) {
    return key !== null && ["ArrowDown", "ArrowUp", "ArrowLeft", "ArrowRight"].includes(key)
}
const InkTextBoxElementBase = InkTextObserverMixin(CrLitElement);
class InkTextBoxElement extends InkTextBoxElementBase {
    static get is() {
        return "ink-text-box"
    }
    static get styles() {
        return getCss$y()
    }
    render() {
        return getHtml$s.bind(this)()
    }
    static get properties() {
        return {
            height_: {
                type: Number
            },
            locationX_: {
                type: Number
            },
            locationY_: {
                type: Number
            },
            minHeight_: {
                type: Number
            },
            minWidth_: {
                type: Number
            },
            state_: {
                type: Number
            },
            textOrientation_: {
                type: Number
            },
            textRotations_: {
                type: Number,
                reflect: true
            },
            textValue_: {
                type: String
            },
            viewportRotations_: {
                type: Number
            },
            width_: {
                type: Number
            },
            zoom_: {
                type: Number
            },
            viewport: {
                type: Object
            },
            annotation: {
                type: Object
            },
            pageDimensions: {
                type: Object
            },
            isPaste: {
                type: Boolean
            }
        }
    }
    #locationX__accessor_storage = 0;
    get locationX_() {
        return this.#locationX__accessor_storage
    }
    set locationX_(value) {
        this.#locationX__accessor_storage = value
    }
    #locationY__accessor_storage = 0;
    get locationY_() {
        return this.#locationY__accessor_storage
    }
    set locationY_(value) {
        this.#locationY__accessor_storage = value
    }
    #minHeight__accessor_storage = MIN_TEXTBOX_SIZE_PX;
    get minHeight_() {
        return this.#minHeight__accessor_storage
    }
    set minHeight_(value) {
        this.#minHeight__accessor_storage = value
    }
    #minWidth__accessor_storage = MIN_TEXTBOX_SIZE_PX;
    get minWidth_() {
        return this.#minWidth__accessor_storage
    }
    set minWidth_(value) {
        this.#minWidth__accessor_storage = value
    }
    #height__accessor_storage = MIN_TEXTBOX_SIZE_PX;
    get height_() {
        return this.#height__accessor_storage
    }
    set height_(value) {
        this.#height__accessor_storage = value
    }
    #state__accessor_storage = TextBoxState.INACTIVE;
    get state_() {
        return this.#state__accessor_storage
    }
    set state_(value) {
        this.#state__accessor_storage = value
    }
    #textOrientation__accessor_storage = 0;
    get textOrientation_() {
        return this.#textOrientation__accessor_storage
    }
    set textOrientation_(value) {
        this.#textOrientation__accessor_storage = value
    }
    #textRotations__accessor_storage = 0;
    get textRotations_() {
        return this.#textRotations__accessor_storage
    }
    set textRotations_(value) {
        this.#textRotations__accessor_storage = value
    }
    #textValue__accessor_storage = "";
    get textValue_() {
        return this.#textValue__accessor_storage
    }
    set textValue_(value) {
        this.#textValue__accessor_storage = value
    }
    #viewportRotations__accessor_storage = 0;
    get viewportRotations_() {
        return this.#viewportRotations__accessor_storage
    }
    set viewportRotations_(value) {
        this.#viewportRotations__accessor_storage = value
    }
    #width__accessor_storage = MIN_TEXTBOX_SIZE_PX;
    get width_() {
        return this.#width__accessor_storage
    }
    set width_(value) {
        this.#width__accessor_storage = value
    }
    #zoom__accessor_storage = 1;
    get zoom_() {
        return this.#zoom__accessor_storage
    }
    set zoom_(value) {
        this.#zoom__accessor_storage = value
    }
    #isPaste_accessor_storage = false;
    get isPaste() {
        return this.#isPaste_accessor_storage
    }
    set isPaste(value) {
        this.#isPaste_accessor_storage = value
    }
    #viewport_accessor_storage = null;
    get viewport() {
        return this.#viewport_accessor_storage
    }
    set viewport(value) {
        this.#viewport_accessor_storage = value
    }
    #annotation_accessor_storage = null;
    get annotation() {
        return this.#annotation_accessor_storage
    }
    set annotation(value) {
        this.#annotation_accessor_storage = value
    }
    #pageDimensions_accessor_storage = null;
    get pageDimensions() {
        return this.#pageDimensions_accessor_storage
    }
    set pageDimensions(value) {
        this.#pageDimensions_accessor_storage = value
    }
    activeKey_ = null;
    arrowKeyDownCount_ = -1;
    attributes_;
    dragTarget_ = null;
    eventTracker_ = new EventTracker;
    existing_ = false;
    id_ = -1;
    pageIndex_ = -1;
    pageHeight_ = 0;
    pageWidth_ = 0;
    pageX_ = 0;
    pageY_ = 0;
    pointerStart_ = null;
    promiseResolver_ = null;
    startPosition_ = null;
    connectedCallback() {
        super.connectedCallback();
        this.eventTracker_.add(this, "pointerdown", (e => this.onPointerDown_(e)));
        this.eventTracker_.add(this, "keydown", (e => this.onKeyDown_(e)))
    }
    disconnectedCallback() {
        super.disconnectedCallback();
        this.eventTracker_.removeAll()
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("annotation") || changedProperties.has("pageDimensions")) {
            if (this.annotation && this.pageDimensions) {
                this.initializeFromProperties_()
            } else {
                this.state_ = TextBoxState.INACTIVE
            }
        }
        const changedPrivateProperties = changedProperties;
        if (changedPrivateProperties.has("minHeight_")) {
            this.height_ = this.getClampedHeight_(this.height_)
        }
        if (changedPrivateProperties.has("minWidth_")) {
            this.width_ = this.getClampedWidth_(this.width_)
        }
        if (changedPrivateProperties.has("state_")) {
            this.hidden = this.state_ === TextBoxState.INACTIVE;
            this.fire("state-changed", this.state_)
        }
        if (changedPrivateProperties.has("viewportRotations_") || changedPrivateProperties.has("textOrientation_")) {
            this.textRotations_ = (this.viewportRotations_ + this.textOrientation_) % 4
        }
    }
    firstUpdated(changedProperties) {
        super.firstUpdated(changedProperties);
        this.setAttribute("tabindex", "0");
        this.addEventListener("focus", (e => this.onFocus_(e)));
        document.addEventListener("keydown", (e => this.onDocumentKeyDown_(e)))
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        const changedPrivateProperties = changedProperties;
        if (changedPrivateProperties.has("width_")) {
            this.$.textbox.style.width = `${this.width_}px`
        }
        if (changedPrivateProperties.has("height_")) {
            this.$.textbox.style.height = `${this.height_}px`
        }
        if (changedPrivateProperties.has("locationX_")) {
            this.style.setProperty("--textbox-location-x", `${this.locationX_}px`)
        }
        if (changedPrivateProperties.has("locationY_")) {
            this.style.setProperty("--textbox-location-y", `${this.locationY_}px`)
        }
        if (changedPrivateProperties.has("zoom_")) {
            this.styleFontSize_()
        }
        if (changedPrivateProperties.has("width_") && this.textRotations_ % 2 === 0 || changedPrivateProperties.has("height_") && this.textRotations_ % 2 === 1) {
            this.updateMinimumSize_()
        }
    }
    styleFontSize_() {
        if (this.attributes_) {
            this.$.textbox.style.fontSize = `${this.attributes_.size * this.zoom_}px`
        }
    }
    onFocus_(e) {
        if (e.relatedTarget === this || e.currentTarget === this && e.relatedTarget === this.$.textbox) {
            return
        }
        this.fire("textbox-focused", {
            height: this.height_,
            locationX: this.locationX_,
            locationY: this.locationY_,
            width: this.width_
        })
    }
    onTextValueInput_() {
        this.textValue_ = this.$.textbox.value;
        this.textBoxEdited_();
        this.updateMinimumSize_()
    }
    createClipboardAnnotation_() {
        if (!this.viewport || !this.attributes_ || this.textValue_ === "") {
            return null
        }
        const pageRect = screenToPageCoordinates(this.pageIndex_, {
            height: this.height_,
            locationX: this.locationX_,
            locationY: this.locationY_,
            width: this.width_
        }, this.viewport);
        return {
            id: this.id_,
            mojoTextInfo: new ArrayBuffer(0),
            pageIndex: this.pageIndex_,
            pdfZoom: this.zoom_,
            text: this.textValue_,
            textAttributes: structuredClone(this.attributes_),
            textBoxRect: pageRect,
            textOrientation: this.textOrientation_,
            viewportOrientation: this.viewportRotations_
        }
    }
    copyAnnotation_() {
        const annotation = this.createClipboardAnnotation_();
        if (!annotation) {
            return
        }
        Ink2Manager.getInstance().saveAnnotationToClipboard(annotation, false)
    }
    cutAnnotation_() {
        const annotation = this.createClipboardAnnotation_();
        if (!annotation) {
            return
        }
        Ink2Manager.getInstance().saveAnnotationToClipboard(annotation, true);
        this.textValue_ = "";
        this.$.textbox.value = "";
        this.textBoxEdited_();
        this.commitTextAnnotation()
    }
    textBoxEdited_() {
        if (this.state_ === TextBoxState.NEW) {
            this.state_ = TextBoxState.EDITED
        }
    }
    updateMinimumSize_() {
        if (this.textRotations_ % 2 === 0) {
            this.$.textbox.style.height = "auto";
            const scrollHeight = this.$.textbox.scrollHeight;
            this.minHeight_ = Math.max(MIN_TEXTBOX_SIZE_PX, scrollHeight);
            this.$.textbox.style.height = `${this.height_}px`
        } else {
            this.$.textbox.style.width = "auto";
            const scrollWidth = this.$.textbox.scrollWidth;
            this.minWidth_ = Math.max(MIN_TEXTBOX_SIZE_PX, scrollWidth);
            this.$.textbox.style.width = `${this.width_}px`
        }
    }
    removePointerDragListeners_() {
        assert(this.dragTarget_);
        this.eventTracker_.remove(this.dragTarget_, "pointercancel");
        this.eventTracker_.remove(this.dragTarget_, "pointerup");
        this.eventTracker_.remove(this.dragTarget_, "pointermove");
        this.dragTarget_ = null;
        this.pointerStart_ = null
    }
    removeKeyDragListeners_() {
        assert(this.dragTarget_);
        this.eventTracker_.remove(this.dragTarget_, "keyup");
        this.eventTracker_.remove(this.dragTarget_, "focusout");
        this.dragTarget_ = null;
        this.activeKey_ = null;
        this.arrowKeyDownCount_ = -1
    }
    addKeyDragListeners_() {
        this.dragTarget_ = this;
        this.startPosition_ = {
            locationX: this.locationX_,
            locationY: this.locationY_,
            width: this.width_,
            height: this.height_
        };
        this.eventTracker_.add(this, "keyup", ( () => this.onHandleKeyUp_()));
        this.eventTracker_.add(this, "focusout", ( () => this.onHandleKeyUp_()))
    }
    resetDrag_() {
        if (this.dragTarget_ === null) {
            return
        }
        assert(this.startPosition_);
        this.locationX_ = this.startPosition_.locationX;
        this.locationY_ = this.startPosition_.locationY;
        this.width_ = this.startPosition_.width;
        this.height_ = this.startPosition_.height;
        this.startPosition_ = null;
        if (this.pointerStart_ !== null) {
            this.removePointerDragListeners_()
        } else if (this.activeKey_ !== null) {
            this.removeKeyDragListeners_()
        }
    }
    commitTextAnnotation() {
        if (this.promiseResolver_) {
            return this.promiseResolver_.promise
        }
        this.promiseResolver_ = new PromiseResolver;
        const promise = this.promiseResolver_.promise;
        this.resetDrag_();
        const hasTextValue = this.textValue_ !== "";
        const isUnedited = this.state_ !== TextBoxState.EDITED && !this.isPaste;
        if ((!hasTextValue || isUnedited) && !this.existing_) {
            this.finishCommit_();
            record(UserAction.ADD_INK2_TEXT_ANNOTATION_ABORTED);
            return promise
        }
        assert(this.attributes_);
        const isEdited = this.state_ === TextBoxState.EDITED;
        const annotation = {
            id: this.id_,
            mojoTextInfo: new ArrayBuffer(0),
            pageIndex: this.pageIndex_,
            pdfZoom: this.zoom_,
            text: this.textValue_,
            textAttributes: structuredClone(this.attributes_),
            textBoxRect: {
                height: this.height_,
                locationX: this.locationX_,
                locationY: this.locationY_,
                width: this.width_
            },
            textOrientation: this.textOrientation_,
            viewportOrientation: this.viewportRotations_
        };
        if (!isEdited) {
            Ink2Manager.getInstance().commitTextAnnotation(annotation, isEdited, []);
            this.finishCommit_();
            record(UserAction.EDIT_INK2_TEXT_ANNOTATION_ABORTED);
            return promise
        }
        (async () => {
            try {
                const result = await PdfViewerPrivateProxyImpl.getInstance().getTextInfo(this.$.textbox, Ink2Manager.getInstance().getKnownFontIds());
                for (const typeface of result.typefaces) {
                    Ink2Manager.getInstance().addKnownFontId(typeface.uniqueId)
                }
                annotation.mojoTextInfo = result.mojoTextInfo;
                Ink2Manager.getInstance().commitTextAnnotation(annotation, isEdited, result.typefaces);
                let action;
                if (this.existing_) {
                    action = hasTextValue ? UserAction.EDIT_INK2_TEXT_ANNOTATION : action = UserAction.DELETE_INK2_TEXT_ANNOTATION
                } else {
                    action = UserAction.ADD_INK2_TEXT_ANNOTATION
                }
                record(action)
            } catch (e) {
                console.error("Error committing text annotation:", e)
            } finally {
                this.finishCommit_()
            }
        }
        )();
        return promise
    }
    finishCommit_() {
        this.state_ = TextBoxState.INACTIVE;
        assert(this.promiseResolver_);
        this.promiseResolver_.resolve();
        this.promiseResolver_ = null
    }
    initializeFromProperties_() {
        const annotation = this.annotation;
        const pageDimensions = this.pageDimensions;
        if (!annotation || !pageDimensions) {
            return
        }
        if (this.viewport) {
            this.zoom_ = this.viewport.getZoom();
            this.viewportRotations_ = this.viewport.getClockwiseRotations()
        }
        this.pageX_ = pageDimensions.x;
        this.pageY_ = pageDimensions.y;
        this.pageWidth_ = pageDimensions.width;
        this.pageHeight_ = pageDimensions.height;
        this.width_ = annotation.textBoxRect.width;
        this.height_ = annotation.textBoxRect.height;
        this.minHeight_ = MIN_TEXTBOX_SIZE_PX;
        this.minWidth_ = MIN_TEXTBOX_SIZE_PX;
        this.locationX_ = annotation.textBoxRect.locationX;
        this.locationY_ = annotation.textBoxRect.locationY;
        this.state_ = this.isPaste ? TextBoxState.EDITED : TextBoxState.NEW;
        this.existing_ = annotation.text !== "" && !this.isPaste;
        this.textValue_ = annotation.text;
        this.id_ = annotation.id;
        this.pageIndex_ = annotation.pageIndex;
        this.textOrientation_ = annotation.textOrientation;
        this.updateTextAttributes_(annotation.textAttributes);
        this.focusTextboxWhenReady_()
    }
    async focusTextboxWhenReady_() {
        await this.updateComplete;
        setTimeout(( () => {
            if (this.isPaste) {
                this.focus()
            } else {
                this.$.textbox.focus()
            }
            this.fire("textbox-focused-for-test")
        }
        ), 0)
    }
    viewportChanged() {
        if (!this.viewport || this.pageIndex_ === -1) {
            return
        }
        const zoom = this.viewport.getZoom();
        const clockwiseRotations = this.viewport.getClockwiseRotations();
        const pageDimensions = this.viewport.getPageScreenRect(this.pageIndex_);
        const adjusted = {
            locationX: (this.locationX_ - this.pageX_) * zoom / this.zoom_,
            locationY: (this.locationY_ - this.pageY_) * zoom / this.zoom_,
            width: Math.max(this.width_ * zoom / this.zoom_, MIN_TEXTBOX_SIZE_PX),
            height: Math.max(this.height_ * zoom / this.zoom_, MIN_TEXTBOX_SIZE_PX)
        };
        const rotated = convertRotatedCoordinates(adjusted, this.viewportRotations_, clockwiseRotations, pageDimensions.width, pageDimensions.height);
        if (this.viewportRotations_ % 2 !== clockwiseRotations % 2) {
            const min = this.minHeight_;
            this.minHeight_ = this.minWidth_;
            this.minWidth_ = min
        }
        this.locationX_ = rotated.locationX + pageDimensions.x;
        this.locationY_ = rotated.locationY + pageDimensions.y;
        this.width_ = rotated.width;
        this.height_ = rotated.height;
        this.viewportRotations_ = clockwiseRotations;
        this.zoom_ = zoom;
        this.pageX_ = pageDimensions.x;
        this.pageY_ = pageDimensions.y;
        this.pageWidth_ = pageDimensions.width;
        this.pageHeight_ = pageDimensions.height
    }
    onDocumentKeyDown_(e) {
        if (e.key !== "Escape" || this.state_ === TextBoxState.INACTIVE) {
            return
        }
        const target = e.composedPath()[0];
        if (target === this.$.textbox) {
            this.focus();
            this.fire("ink-text-box-focused-for-test")
        } else {
            this.commitTextAnnotation()
        }
        e.preventDefault();
        e.stopPropagation()
    }
    onKeyDown_(e) {
        if (this.state_ === TextBoxState.INACTIVE) {
            return
        }
        const textStyle = getTextStyleForShortcut(e);
        if (textStyle !== null) {
            e.preventDefault();
            e.stopPropagation();
            Ink2Manager.getInstance().toggleTextStyle(textStyle);
            return
        }
        const target = e.composedPath()[0];
        if (!(target instanceof HTMLElement) || target === this.$.textbox) {
            return
        }
        if (hasCtrlModifierOnly(e)) {
            const key = e.key.toLowerCase();
            if (key === "c" || key === "x") {
                e.preventDefault();
                e.stopPropagation();
                if (key === "c") {
                    this.copyAnnotation_()
                } else {
                    this.cutAnnotation_()
                }
                return
            }
        }
        if (e.key === "Backspace" || e.key === "Delete") {
            this.textValue_ = "";
            this.textBoxEdited_();
            this.commitTextAnnotation().then(( () => {
                getInstance().announce(loadTimeData.getString("ink2TextAnnotationDeleted"))
            }
            ));
            return
        }
        if (this.pointerStart_ !== null) {
            return
        }
        if (this.handleResizeShortcut_(e)) {
            e.preventDefault();
            e.stopPropagation();
            return
        }
        if (!isArrowKey(e.key)) {
            return
        }
        if (this.activeKey_ !== null && !isArrowKey(this.activeKey_)) {
            return
        }
        e.preventDefault();
        e.stopPropagation();
        if (this.activeKey_ !== null && this.activeKey_ !== e.key) {
            this.onHandleKeyUp_()
        }
        this.activeKey_ = e.key;
        if (this.arrowKeyDownCount_ === -1) {
            this.addKeyDragListeners_();
            this.arrowKeyDownCount_ = 0
        }
        this.arrowKeyDownCount_++;
        let moveX = 0;
        let moveY = 0;
        switch (e.key) {
        case "ArrowDown":
            moveY = this.arrowKeyDownCount_;
            break;
        case "ArrowUp":
            moveY = -1 * this.arrowKeyDownCount_;
            break;
        case "ArrowLeft":
            moveX = -1 * this.arrowKeyDownCount_;
            break;
        case "ArrowRight":
            moveX = this.arrowKeyDownCount_;
            break
        }
        this.onMove_(this, moveX, moveY)
    }
    announceMoveOrResize_() {
        if (!this.startPosition_) {
            return
        }
        if (this.width_ !== this.startPosition_.width || this.height_ !== this.startPosition_.height) {
            getInstance().announce(loadTimeData.getString("ink2TextAnnotationResized"));
            return
        }
        const deltaX = this.locationX_ - this.startPosition_.locationX;
        if (deltaX !== 0) {
            const stringId = deltaX > 0 ? "ink2TextAnnotationMovedRight" : "ink2TextAnnotationMovedLeft";
            getInstance().announce(loadTimeData.getString(stringId))
        }
        const deltaY = this.locationY_ - this.startPosition_.locationY;
        if (deltaY !== 0) {
            const stringId = deltaY > 0 ? "ink2TextAnnotationMovedDown" : "ink2TextAnnotationMovedUp";
            getInstance().announce(loadTimeData.getString(stringId))
        }
    }
    onHandleKeyUp_() {
        this.announceMoveOrResize_();
        this.startPosition_ = null;
        this.removeKeyDragListeners_();
        this.textBoxEdited_()
    }
    onPointerDown_(e) {
        const target = e.composedPath()[0];
        if (e.button !== 0 || !(target instanceof HTMLElement) || target === this.$.textbox) {
            return
        }
        if (this.dragTarget_ !== null) {
            return
        }
        this.dragTarget_ = target;
        this.pointerStart_ = {
            x: e.x,
            y: e.y
        };
        this.startPosition_ = {
            locationX: this.locationX_,
            locationY: this.locationY_,
            width: this.width_,
            height: this.height_
        };
        this.eventTracker_.add(target, "pointercancel", ( () => this.onHandlePointerUp_()));
        this.eventTracker_.add(target, "pointerup", ( () => this.onHandlePointerUp_()));
        this.eventTracker_.add(target, "pointermove", (e => this.onHandlePointerMove_(e)));
        target.setPointerCapture(e.pointerId)
    }
    onHandlePointerMove_(e) {
        const target = e.target;
        assert(this.pointerStart_);
        this.onMove_(target, e.x - this.pointerStart_.x, e.y - this.pointerStart_.y)
    }
    onMove_(target, moveX, moveY) {
        assert(this.startPosition_);
        if (!target.classList.contains("handle")) {
            this.locationX_ = Math.min(this.pageX_ + this.pageWidth_ - this.width_, Math.max(this.pageX_, this.startPosition_.locationX + moveX));
            this.locationY_ = Math.min(this.pageY_ + this.pageHeight_ - this.height_, Math.max(this.pageY_, this.startPosition_.locationY + moveY));
            return
        }
        if (target.classList.contains("left")) {
            const deltaX = Math.max(this.pageX_ - this.startPosition_.locationX, Math.min(moveX, this.startPosition_.width - this.minWidth_));
            this.locationX_ = this.startPosition_.locationX + deltaX;
            this.width_ = this.startPosition_.width - deltaX
        } else if (target.classList.contains("right")) {
            this.width_ = this.getClampedWidth_(this.startPosition_.width + moveX)
        }
        if (target.classList.contains("top")) {
            const deltaY = Math.max(this.pageY_ - this.startPosition_.locationY, Math.min(moveY, this.startPosition_.height - this.minHeight_));
            this.locationY_ = this.startPosition_.locationY + deltaY;
            this.height_ = this.startPosition_.height - deltaY
        } else if (target.classList.contains("bottom")) {
            this.height_ = this.getClampedHeight_(this.startPosition_.height + moveY)
        }
    }
    onHandlePointerUp_() {
        this.announceMoveOrResize_();
        this.startPosition_ = null;
        this.removePointerDragListeners_();
        this.textBoxEdited_()
    }
    updateTextAttributes_(newAttributes) {
        this.$.textbox.style.fontFamily = getStyleForTypeface(newAttributes.typeface);
        this.attributes_ = newAttributes;
        this.styleFontSize_();
        this.$.textbox.style.textAlign = newAttributes.alignment;
        this.$.textbox.style.fontStyle = newAttributes.styles.italic ? "italic" : "normal";
        this.$.textbox.style.fontWeight = newAttributes.styles.bold ? "bold" : "normal";
        this.$.textbox.style.color = colorToHex(newAttributes.color);
        const decorations = [];
        if (newAttributes.styles.underline) {
            decorations.push("underline")
        }
        if (newAttributes.styles.strikethrough) {
            decorations.push("line-through")
        }
        this.$.textbox.style.textDecoration = decorations.join(" ") || "none"
    }
    onTextAttributesChanged(newAttributes) {
        if (!!this.attributes_ && newAttributes.typeface === this.attributes_.typeface && newAttributes.size === this.attributes_.size && colorsEqual(newAttributes.color, this.attributes_.color) && newAttributes.alignment === this.attributes_.alignment && stylesEqual(newAttributes.styles, this.attributes_.styles)) {
            return
        }
        this.updateTextAttributes_(newAttributes);
        this.textBoxEdited_();
        if (this.state_ !== TextBoxState.INACTIVE) {
            this.updateMinimumSize_()
        }
    }
    handleResizeShortcut_(e) {
        if (this.state_ === TextBoxState.INACTIVE || this.pointerStart_ !== null || isArrowKey(this.activeKey_)) {
            return false
        }
        const mainModifier = hasCtrlModifier(e);
        const secondModifier = isMac ? e.ctrlKey : e.altKey;
        if (!mainModifier || !secondModifier || e.shiftKey) {
            return false
        }
        const key = e.key.toLowerCase();
        if (!["b", "w", "i", "9", "k", "j"].includes(key)) {
            return false
        }
        if (this.activeKey_ !== null && this.activeKey_ !== key) {
            this.onHandleKeyUp_()
        }
        if (this.activeKey_ === null) {
            this.activeKey_ = key;
            this.addKeyDragListeners_()
        }
        switch (key) {
        case "b":
            this.resizeBy_(KEYBOARD_RESIZE_STEP_PX, 0);
            return true;
        case "w":
            this.resizeBy_(-KEYBOARD_RESIZE_STEP_PX, 0);
            return true;
        case "i":
            this.resizeBy_(0, KEYBOARD_RESIZE_STEP_PX);
            return true;
        case "9":
            this.resizeBy_(0, -KEYBOARD_RESIZE_STEP_PX);
            return true;
        case "k":
            this.resizeProportionally_(1.1);
            return true;
        case "j":
            this.resizeProportionally_(.9);
            return true;
        default:
            assertNotReached()
        }
    }
    resizeBy_(deltaX, deltaY) {
        const newWidth = this.getClampedWidth_(this.width_ + deltaX);
        const newHeight = this.getClampedHeight_(this.height_ + deltaY);
        if (newWidth !== this.width_ || newHeight !== this.height_) {
            this.width_ = newWidth;
            this.height_ = newHeight
        }
    }
    resizeProportionally_(scale) {
        const clampedScale = scale > 1 ? Math.min(scale, this.getMaxWidth_() / this.width_, this.getMaxHeight_() / this.height_) : Math.max(scale, this.minWidth_ / this.width_, this.minHeight_ / this.height_);
        const newWidth = Math.round(this.width_ * clampedScale);
        const newHeight = Math.round(this.height_ * clampedScale);
        if (newWidth !== this.width_ || newHeight !== this.height_) {
            this.width_ = newWidth;
            this.height_ = newHeight
        }
    }
    getMaxWidth_() {
        return this.pageWidth_ + this.pageX_ - this.locationX_
    }
    getMaxHeight_() {
        return this.pageHeight_ + this.pageY_ - this.locationY_
    }
    getClampedWidth_(width) {
        return Math.min(this.getMaxWidth_(), Math.max(this.minWidth_, width))
    }
    getClampedHeight_(height) {
        return Math.min(this.getMaxHeight_(), Math.max(this.minHeight_, height))
    }
}
customElements.define(InkTextBoxElement.is, InkTextBoxElement);
let instance$y = null;
function getCss$x() {
    return instance$y || (instance$y = [...[], css`:host{display:block;left:0;overflow:hidden;pointer-events:none;position:absolute;top:0;z-index:1}#container{display:block;height:100%;overflow:hidden;position:relative;width:100%;z-index:0}.placeholder{position:absolute;border:var(--viewer-text-annotation-border-width) solid transparent;box-sizing:border-box;outline:none;--offset-x:var(--viewer-text-annotation-offset-x);--offset-y:var(--viewer-text-annotation-offset-y);--padding-x:var(--viewer-text-annotation-padding-x);--padding-y:var(--viewer-text-annotation-padding-y);left:calc(var(--left,0px) - var(--offset-x));top:calc(var(--top,0px) - var(--offset-y));width:calc(var(--width,0px) + var(--padding-x));height:calc(var(--height,0px) + var(--padding-y))}.placeholder[data-rotations='1'],.placeholder[data-rotations='3']{--offset-x:var(--viewer-text-annotation-offset-x-rotated);--offset-y:var(--viewer-text-annotation-offset-y-rotated);--padding-x:var(--viewer-text-annotation-padding-x-rotated);--padding-y:var(--viewer-text-annotation-padding-y-rotated)}.placeholder:focus-visible{border-color:var(--viewer-text-annotation-active-color)}ink-text-box{pointer-events:auto}`])
}
function getHtml$r() {
    return html`<!--_html_template_start_-->
<div id="container" role="list" aria-label="Annotation"
    @focusout="${this.onContainerFocusout_}">
  ${this.placeholders_.map(( (placeholder, index) => html`
    <div class="placeholder" style="${this.getStyles_(placeholder)}"
        data-index="${index}" data-rotations="${placeholder.rotations}"
        aria-hidden="${this.isPlaceholderAriaHidden_(placeholder)}"
        aria-setsize="${this.placeholders_.length}" aria-posinset="${index + 1}"
        role="listitem" aria-label="${placeholder.label}"
        tabindex="${this.getPlaceholderTabIndex_(placeholder)}"
        @focus="${this.onPlaceholderFocus_}"
        @keydown="${this.onPlaceholderKeydown_}">
    </div>
  `))}
</div>
<ink-text-box id="textBox" .viewport="${this.viewport}"
    .annotation="${this.activeAnnotation_}"
    .pageDimensions="${this.activePageDimensions_}" .isPaste="${this.isPaste_}"
    @state-changed="${this.onTextBoxStateChanged_}"
    @textbox-focused="${this.onTextboxFocused_}">
</ink-text-box>
<!--_html_template_end_-->`
}
class InkTextAnnotationsElement extends CrLitElement {
    static get is() {
        return "ink-text-annotations"
    }
    static get styles() {
        return getCss$x()
    }
    render() {
        return getHtml$r.bind(this)()
    }
    static get properties() {
        return {
            viewport: {
                type: Object
            },
            activeAnnotation_: {
                type: Object
            },
            activePageDimensions_: {
                type: Object
            },
            focusedIndex_: {
                type: Number
            },
            isPaste_: {
                type: Boolean
            },
            placeholders_: {
                type: Array
            }
        }
    }
    #viewport_accessor_storage = null;
    get viewport() {
        return this.#viewport_accessor_storage
    }
    set viewport(value) {
        this.#viewport_accessor_storage = value
    }
    #activeAnnotation__accessor_storage = null;
    get activeAnnotation_() {
        return this.#activeAnnotation__accessor_storage
    }
    set activeAnnotation_(value) {
        this.#activeAnnotation__accessor_storage = value
    }
    #activePageDimensions__accessor_storage = null;
    get activePageDimensions_() {
        return this.#activePageDimensions__accessor_storage
    }
    set activePageDimensions_(value) {
        this.#activePageDimensions__accessor_storage = value
    }
    #focusedIndex__accessor_storage = -1;
    get focusedIndex_() {
        return this.#focusedIndex__accessor_storage
    }
    set focusedIndex_(value) {
        this.#focusedIndex__accessor_storage = value
    }
    #isPaste__accessor_storage = false;
    get isPaste_() {
        return this.#isPaste__accessor_storage
    }
    set isPaste_(value) {
        this.#isPaste__accessor_storage = value
    }
    #placeholders__accessor_storage = [];
    get placeholders_() {
        return this.#placeholders__accessor_storage
    }
    set placeholders_(value) {
        this.#placeholders__accessor_storage = value
    }
    annotations_ = [];
    eventTracker_ = new EventTracker;
    connectedCallback() {
        super.connectedCallback();
        const manager = Ink2Manager.getInstance();
        this.eventTracker_.add(manager, "annotations-updated", ( () => this.updateAnnotations_()));
        this.eventTracker_.add(manager, "initialize-text-box", (e => this.onInitializeTextBox_(e.detail)));
        this.eventTracker_.add(this, "wheel", (e => this.onWheel_(e)));
        this.eventTracker_.add(document, "keydown", (e => this.onKeyDown_(e)));
        this.updateAnnotations_()
    }
    disconnectedCallback() {
        super.disconnectedCallback();
        this.eventTracker_.removeAll()
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        const changedPrivateProperties = changedProperties;
        if (changedPrivateProperties.has("focusedIndex_")) {
            this.updatePlaceholders_()
        }
    }
    onKeyDown_(e) {
        if (!hasCtrlModifierOnly(e) || e.key.toLowerCase() !== "v") {
            return
        }
        const target = e.composedPath()[0] ?? null;
        if (target instanceof HTMLTextAreaElement || target instanceof HTMLInputElement) {
            return
        }
        this.pasteAnnotation()
    }
    async pasteAnnotation() {
        if (this.activeAnnotation_) {
            await this.$.textBox.commitTextAnnotation()
        }
        Ink2Manager.getInstance().pasteAnnotation()
    }
    viewportChanged() {
        this.updatePlaceholders_();
        this.$.textBox.viewportChanged()
    }
    updateAnnotations_() {
        const manager = Ink2Manager.getInstance();
        const allAnnotations = [];
        const sortedPages = Array.from(manager.annotations.keys()).sort(( (a, b) => a - b));
        for (const page of sortedPages) {
            const pageAnnotationsMap = manager.annotations.get(page);
            if (!pageAnnotationsMap || pageAnnotationsMap.size === 0) {
                continue
            }
            const pageAnnotations = Array.from(pageAnnotationsMap.values());
            pageAnnotations.sort(( (a, b) => {
                if (a.textBoxRect.locationY !== b.textBoxRect.locationY) {
                    return a.textBoxRect.locationY - b.textBoxRect.locationY
                }
                return a.textBoxRect.locationX - b.textBoxRect.locationX
            }
            ));
            allAnnotations.push(...pageAnnotations)
        }
        this.annotations_ = allAnnotations;
        this.updatePlaceholders_()
    }
    getActiveWindowIndices_() {
        const indices = new Set;
        const total = this.annotations_.length;
        if (total === 0) {
            return indices
        }
        if (this.focusedIndex_ === -1) {
            indices.add(0);
            indices.add(total - 1);
            return indices
        }
        if (this.focusedIndex_ > 0) {
            indices.add(this.focusedIndex_ - 1)
        }
        indices.add(this.focusedIndex_);
        if (this.focusedIndex_ < total - 1) {
            indices.add(this.focusedIndex_ + 1)
        }
        return indices
    }
    updatePlaceholders_() {
        const viewport = this.viewport;
        assert(viewport);
        const activeIndices = this.getActiveWindowIndices_();
        const clockwiseRotations = viewport.getClockwiseRotations();
        this.placeholders_ = this.annotations_.map(( (annotation, index) => {
            const screenRect = activeIndices.has(index) ? pageToScreenCoordinates(annotation.pageIndex, annotation.textBoxRect, viewport) : null;
            return {
                screenRect: screenRect,
                label: annotation.text,
                rotations: (clockwiseRotations + annotation.textOrientation) % 4
            }
        }
        ))
    }
    getStyles_(placeholder) {
        if (!placeholder.screenRect) {
            return "opacity: 0;"
        }
        return `\n      --left: ${placeholder.screenRect.locationX}px;\n      --top: ${placeholder.screenRect.locationY}px;\n      --width: ${placeholder.screenRect.width}px;\n      --height: ${placeholder.screenRect.height}px;\n    `
    }
    onPlaceholderFocus_(e) {
        const currentTarget = e.currentTarget;
        const index = Number(currentTarget.dataset["index"]);
        this.focusedIndex_ = index;
        const placeholder = this.placeholders_[index];
        assert(placeholder);
        assert(placeholder.screenRect);
        this.scrollToShowTextBox_(placeholder.screenRect)
    }
    onContainerFocusout_(e) {
        const relatedTarget = e.relatedTarget;
        if (!this.$.container.contains(relatedTarget)) {
            this.focusedIndex_ = -1
        }
    }
    async onPlaceholderKeydown_(e) {
        if (e.key !== "Enter" && e.key !== " ") {
            return
        }
        e.preventDefault();
        const index = Number(e.currentTarget.dataset["index"]);
        const annotation = this.annotations_[index];
        assert(annotation);
        if (this.activeAnnotation_) {
            if (this.activeAnnotation_.id === annotation.id) {
                return
            }
            await this.$.textBox.commitTextAnnotation()
        }
        Ink2Manager.getInstance().activateAnnotationById(annotation.id)
    }
    commitActiveAnnotation() {
        return this.$.textBox.commitTextAnnotation()
    }
    blurActiveAnnotation() {
        this.$.textBox.blur()
    }
    onTextBoxStateChanged_(e) {
        if (e.detail === TextBoxState.INACTIVE) {
            this.isPaste_ = false;
            this.activeAnnotation_ = null;
            this.activePageDimensions_ = null;
            this.focusedIndex_ = -1
        }
        this.fire("state-changed", e.detail)
    }
    async onInitializeTextBox_(data) {
        if (this.activeAnnotation_) {
            await this.$.textBox.commitTextAnnotation()
        }
        this.isPaste_ = !!data.isPaste;
        this.activeAnnotation_ = data.annotation;
        this.activePageDimensions_ = data.pageDimensions
    }
    onTextboxFocused_(e) {
        this.scrollToShowTextBox_(e.detail)
    }
    getPlaceholderTabIndex_(placeholder) {
        if (this.activeAnnotation_ || !placeholder.screenRect) {
            return -1
        }
        return 0
    }
    isPlaceholderAriaHidden_(placeholder) {
        return this.activeAnnotation_ || !placeholder.screenRect ? "true" : "false"
    }
    onWheel_(e) {
        assert(this.viewport);
        if (e.ctrlKey) {
            return
        }
        e.preventDefault();
        this.viewport.scrollBy({
            x: e.deltaX,
            y: e.deltaY
        })
    }
    scrollToShowTextBox_(textBoxRect) {
        this.$.container.scrollTop = 0;
        this.$.container.scrollLeft = 0;
        this.scrollTop = 0;
        this.scrollLeft = 0;
        assert(this.viewport);
        const viewportPosition = this.viewport.position;
        const viewportSize = this.viewport.size;
        let scrollX;
        let scrollY;
        if (textBoxRect.locationX < 0 || textBoxRect.locationX + textBoxRect.width > viewportSize.width) {
            scrollX = viewportPosition.x + textBoxRect.locationX - Math.floor(viewportSize.width / 10)
        }
        if (textBoxRect.locationY < 0 || textBoxRect.locationY + textBoxRect.height > viewportSize.height) {
            scrollY = viewportPosition.y + textBoxRect.locationY - Math.floor(viewportSize.height / 10)
        }
        if (scrollX !== undefined || scrollY !== undefined) {
            this.viewport.scrollTo({
                x: scrollX,
                y: scrollY
            })
        }
    }
}
customElements.define(InkTextAnnotationsElement.is, InkTextAnnotationsElement);
let instance$x = null;
function getCss$w() {
    return instance$x || (instance$x = [...[], css`:host{display:inline-block}cr-radio-group{--cr-radio-group-item-padding:0;display:flex;gap:16px;justify-content:center}`])
}
function getHtml$q() {
    return html`<!--_html_template_start_-->
<cr-radio-group aria-label="Text alignment"
    selectable-elements="selectable-icon-button"
    .selected="${this.currentAlignment_}"
    @keydown="${this.onAlignmentKeydown_}">
  <selectable-icon-button icon="pdf-ink:format-align-left"
      name="${TextAlignment.LEFT}" label="Left"
      @click="${this.onAlignmentClick_}">
  </selectable-icon-button>
  <selectable-icon-button icon="pdf-ink:format-align-center"
      name="${TextAlignment.CENTER}" label="Center"
      @click="${this.onAlignmentClick_}">
  </selectable-icon-button>
  <selectable-icon-button icon="pdf-ink:format-align-right"
      name="${TextAlignment.RIGHT}" label="Right"
      @click="${this.onAlignmentClick_}">
  </selectable-icon-button>
</cr-radio-group>
<!--_html_template_end_-->`
}
const TextAlignmentSelectorElementBase = InkTextObserverMixin(CrLitElement);
class TextAlignmentSelectorElement extends TextAlignmentSelectorElementBase {
    static get is() {
        return "text-alignment-selector"
    }
    static get styles() {
        return getCss$w()
    }
    render() {
        return getHtml$q.bind(this)()
    }
    static get properties() {
        return {
            currentAlignment_: {
                type: String
            }
        }
    }
    #currentAlignment__accessor_storage = TextAlignment.LEFT;
    get currentAlignment_() {
        return this.#currentAlignment__accessor_storage
    }
    set currentAlignment_(value) {
        this.#currentAlignment__accessor_storage = value
    }
    focus() {
        const selectedButton = this.shadowRoot.querySelector("selectable-icon-button[checked]");
        assert(selectedButton);
        selectedButton.focus()
    }
    onAlignmentClick_(e) {
        const button = e.currentTarget;
        const newAlignment = button.getAttribute("name");
        assert(newAlignment);
        this.setAlignment_(newAlignment)
    }
    onAlignmentKeydown_(e) {
        if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End", " ", "Enter"].includes(e.key)) {
            return
        }
        setTimeout(( () => {
            const radioGroup = this.shadowRoot.querySelector("cr-radio-group");
            assert(radioGroup);
            if (radioGroup.selected) {
                this.setAlignment_(radioGroup.selected)
            }
        }
        ), 0)
    }
    setAlignment_(newAlignment) {
        if (newAlignment === this.currentAlignment_) {
            return
        }
        this.currentAlignment_ = newAlignment;
        Ink2Manager.getInstance().setTextAlignment(newAlignment)
    }
    onTextAttributesChanged(attributes) {
        this.currentAlignment_ = attributes.alignment
    }
}
customElements.define(TextAlignmentSelectorElement.is, TextAlignmentSelectorElement);
let instance$w = null;
function getCss$v() {
    return instance$w || (instance$w = [...[], css`:host{display:flex;gap:var(--text-styles-selector-gap,16px)}cr-icon-button{--cr-icon-button-fill-color:var(--viewer-icon-ink-fill-color);--cr-icon-button-focus-outline-color:var(--viewer-icon-focus-outline-color);--cr-icon-button-margin-end:0;--cr-icon-button-margin-start:0}cr-icon-button.active{--cr-icon-button-fill-color:var(--viewer-icon-ink-selected-fill-color);background-color:var(--viewer-icon-ink-selected-background-color);border-radius:50%}`])
}
function getHtml$p() {
    return html`<!--_html_template_start_-->
${this.getTextStyles_().map((style => html`
  <cr-icon-button class="${this.getActiveClass_(style)}"
      @click="${this.onStyleButtonClick_}" data-style="${style}"
      iron-icon="${this.getIcon_(style)}"
      aria-pressed="${this.getAriaPressed_(style)}"
      aria-label="${this.getTitle_(style)}" title="${this.getTitle_(style)}">
  </cr-icon-button>
`))}
<!--_html_template_end_-->`
}
const TextStylesSelectorElementBase = InkTextObserverMixin(I18nMixinLit(CrLitElement));
class TextStylesSelectorElement extends TextStylesSelectorElementBase {
    static get is() {
        return "text-styles-selector"
    }
    static get styles() {
        return getCss$v()
    }
    render() {
        return getHtml$p.bind(this)()
    }
    static get properties() {
        return {
            currentStyles_: {
                type: Object
            }
        }
    }
    #currentStyles__accessor_storage = {
        [TextStyle.BOLD]: false,
        [TextStyle.ITALIC]: false,
        [TextStyle.UNDERLINE]: false,
        [TextStyle.STRIKETHROUGH]: false
    };
    get currentStyles_() {
        return this.#currentStyles__accessor_storage
    }
    set currentStyles_(value) {
        this.#currentStyles__accessor_storage = value
    }
    getTextStyles_() {
        if (loadTimeData.getBoolean("pdfTextAnnotationsExtraStylesEnabled")) {
            return Object.values(TextStyle)
        }
        return [TextStyle.BOLD, TextStyle.ITALIC]
    }
    onStyleButtonClick_(e) {
        const style = e.target.dataset["style"];
        Ink2Manager.getInstance().toggleTextStyle(style)
    }
    getActiveClass_(style) {
        return this.currentStyles_[style] ? "active" : ""
    }
    getAriaPressed_(style) {
        return this.currentStyles_[style] ? "true" : "false"
    }
    getIcon_(style) {
        switch (style) {
        case TextStyle.BOLD:
            return "pdf-ink:format-bold";
        case TextStyle.ITALIC:
            return "pdf-ink:format-italic";
        case TextStyle.STRIKETHROUGH:
            return "pdf-ink:strikethrough-s";
        case TextStyle.UNDERLINE:
            return "pdf-ink:format-underlined";
        default:
            assertNotReachedCase()
        }
    }
    getTitle_(style) {
        switch (style) {
        case TextStyle.BOLD:
            return this.i18n("ink2TextStyleBold");
        case TextStyle.ITALIC:
            return this.i18n("ink2TextStyleItalic");
        case TextStyle.STRIKETHROUGH:
            return this.i18n("ink2TextStyleStrikethrough");
        case TextStyle.UNDERLINE:
            return this.i18n("ink2TextStyleUnderline");
        default:
            assertNotReachedCase()
        }
    }
    onTextAttributesChanged(attributes) {
        this.currentStyles_ = attributes.styles
    }
}
customElements.define(TextStylesSelectorElement.is, TextStylesSelectorElement);
let instance$v = null;
function getCss$u() {
    return instance$v || (instance$v = [...[getCss$J()], css`#item{align-items:flex-start;display:flex;padding:5px 28px;position:relative;transition:background-color 100ms ease-out}#item:hover{background-color:rgba(255,255,255,0.25)}#title{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}:host(:not([save-allowed_])) #title{opacity:var(--cr-disabled-opacity)}#download{--cr-icon-button-fill-color:var(--primary-text-color);--cr-icon-button-icon-size:16px;--cr-icon-button-size:28px;margin:0;position:absolute;right:0;top:calc((100% - var(--cr-icon-button-size)) / 2)}#download:focus-visible{outline:auto -webkit-focus-ring-color}`])
}
function getHtml$o() {
    return html`<!--_html_template_start_-->
<div id="item">
  <span id="title">${this.attachment.name}</span>
  <cr-icon-button id="download" tabindex="0" ?hidden="${!this.saveAllowed_}"
      title="Download the attachment" iron-icon="cr:download"
      @click="${this.onDownloadClick_}">
  </cr-icon-button>
</div>
<!--_html_template_end_-->`
}
class ViewerAttachmentElement extends CrLitElement {
    static get is() {
        return "viewer-attachment"
    }
    static get styles() {
        return getCss$u()
    }
    render() {
        return getHtml$o.bind(this)()
    }
    static get properties() {
        return {
            attachment: {
                type: Object
            },
            index: {
                type: Number
            },
            saveAllowed_: {
                type: Boolean,
                reflect: true
            }
        }
    }
    #attachment_accessor_storage = {
        name: "",
        size: 0,
        readable: false
    };
    get attachment() {
        return this.#attachment_accessor_storage
    }
    set attachment(value) {
        this.#attachment_accessor_storage = value
    }
    #index_accessor_storage = -1;
    get index() {
        return this.#index_accessor_storage
    }
    set index(value) {
        this.#index_accessor_storage = value
    }
    #saveAllowed__accessor_storage = false;
    get saveAllowed_() {
        return this.#saveAllowed__accessor_storage
    }
    set saveAllowed_(value) {
        this.#saveAllowed__accessor_storage = value
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("attachment")) {
            this.saveAllowed_ = !!this.attachment && this.attachment.size !== -1
        }
    }
    onDownloadClick_() {
        if (!this.attachment || this.attachment.size === -1) {
            return
        }
        this.fire("save-attachment", this.index)
    }
}
customElements.define(ViewerAttachmentElement.is, ViewerAttachmentElement);
let instance$u = null;
function getCss$t() {
    return instance$u || (instance$u = [...[getCss$E()], css`:host{display:block;padding-inline-end:20px;padding-top:20px}#warning{align-items:flex-start;padding:5px 28px 15px;position:relative}`])
}
function getHtml$n() {
    return html`<!--_html_template_start_-->
<div id="warning" ?hidden="${!this.exceedSizeLimit_()}">
  Files over 100MB are not available for download
</div>
${this.attachments.map(( (item, index) => html`
  <viewer-attachment .attachment="${item}" .index="${index}">
  </viewer-attachment>
`))}
<!--_html_template_end_-->`
}
class ViewerAttachmentBarElement extends CrLitElement {
    static get is() {
        return "viewer-attachment-bar"
    }
    static get styles() {
        return getCss$t()
    }
    render() {
        return getHtml$n.bind(this)()
    }
    static get properties() {
        return {
            attachments: {
                type: Array
            }
        }
    }
    #attachments_accessor_storage = [];
    get attachments() {
        return this.#attachments_accessor_storage
    }
    set attachments(value) {
        this.#attachments_accessor_storage = value
    }
    exceedSizeLimit_() {
        return this.attachments.some((attachment => attachment.size === -1))
    }
}
customElements.define(ViewerAttachmentBarElement.is, ViewerAttachmentBarElement);
let instance$t = null;
function getCss$s() {
    return instance$t || (instance$t = [...[getCss$E()], css`:host{--dropdown-button-size:32px;display:flex;position:relative}cr-button{--cr-focus-outline-color:var(--viewer-icon-focus-outline-color);--iron-icon-fill-color:var(--viewer-icon-ink-fill-color);border:none;height:var(--dropdown-button-size);width:var(--dropdown-button-size);margin:0;min-width:auto}cr-button[data-selected='true']{--iron-icon-fill-color:var(--viewer-icon-ink-selected-fill-color);background-color:var(--viewer-icon-ink-selected-background-color)}div{background-color:var(--viewer-side-background-color);bottom:48px;border-radius:8px;left:50%;margin-bottom:4px;padding:0 8px;position:absolute;transform:translateX(-50%)}`])
}
function getHtml$m() {
    return html`
<cr-button @click="${this.onDropdownClick_}"
    data-selected="${this.showDropdown_}" aria-expanded="${this.showDropdown_}"
    aria-haspopup="true" title="${this.buttonTitle}">
  <slot name="icon"></slot>
</cr-button>
<div>
  ${this.showDropdown_ ? html`
    <slot name="menu"></slot>
  ` : ""}
</div>`
}
class ViewerBottomToolbarDropdownElement extends CrLitElement {
    static get is() {
        return "viewer-bottom-toolbar-dropdown"
    }
    static get styles() {
        return getCss$s()
    }
    render() {
        return getHtml$m.bind(this)()
    }
    static get properties() {
        return {
            buttonTitle: {
                type: String
            },
            showDropdown_: {
                type: Boolean
            }
        }
    }
    #buttonTitle_accessor_storage = "";
    get buttonTitle() {
        return this.#buttonTitle_accessor_storage
    }
    set buttonTitle(value) {
        this.#buttonTitle_accessor_storage = value
    }
    #showDropdown__accessor_storage = false;
    get showDropdown_() {
        return this.#showDropdown__accessor_storage
    }
    set showDropdown_(value) {
        this.#showDropdown__accessor_storage = value
    }
    tracker_ = new EventTracker;
    disconnectedCallback() {
        this.tracker_.removeAll();
        super.disconnectedCallback()
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        const changedPrivateProperties = changedProperties;
        if (changedPrivateProperties.has("showDropdown_") && this.showDropdown_) {
            const menuSlot = this.shadowRoot.querySelector('slot[name="menu"]');
            assert(menuSlot);
            const menuElements = menuSlot.assignedElements();
            if (menuElements.length > 0) {
                menuElements[0].focus()
            }
        }
    }
    onDropdownClick_() {
        this.toggleDropdown_()
    }
    toggleDropdown_() {
        this.showDropdown_ = !this.showDropdown_;
        if (this.showDropdown_) {
            this.tracker_.add(this, "focusout", this.handleFocusOut_.bind(this))
        } else {
            this.tracker_.remove(this, "focusout")
        }
    }
    handleFocusOut_(e) {
        assert(this.showDropdown_);
        const nextElement = e.relatedTarget;
        if (nextElement instanceof HTMLElement && nextElement !== this && this.contains(nextElement)) {
            return
        }
        this.toggleDropdown_()
    }
}
customElements.define(ViewerBottomToolbarDropdownElement.is, ViewerBottomToolbarDropdownElement);
let instance$s = null;
function getCss$r() {
    return instance$s || (instance$s = [...[], css`:host{--toolbar-item-gap:10px;align-items:center;background-color:var(--viewer-side-background-color);bottom:0;border-radius:24px 24px 0 0;display:flex;padding:12px;position:absolute}ink-color-selector{padding:20px}.toolbar-icon{padding:2px}.toolbar-icon:not(:first-child){padding-inline-start:4px}.toolbar-icon:not(:last-child){padding-inline-end:4px}.color-chip{background:var(--ink-brush-color,magenta);border:1px solid var(--viewer-icon-ink-background-color);border-radius:50%;height:20px;width:20px}`])
}
let instance$r = null;
function getCss$q() {
    return instance$r || (instance$r = [...[getCss$E(), getCss$r()], css`:host{--cr-icon-button-margin-end:0;--cr-icon-button-margin-start:0}#vertical-separator{background:rgba(255,255,255,0.3);height:20px;margin-inline:var(--toolbar-item-gap);width:1px}ink-brush-selector{--ink-brush-button-gap:8px;--ink-brush-button-size:32px}`])
}
function getHtml$l() {
    return html`<!--_html_template_start_-->
<ink-brush-selector class="toolbar-icon" .currentType="${this.currentType}"
    @current-type-changed="${this.onCurrentTypeChanged}">
</ink-brush-selector>
${this.shouldShowBrushOptions_() ? html`
  <span id="vertical-separator"></span>
  <viewer-bottom-toolbar-dropdown id="size" class="toolbar-icon"
      .buttonTitle="${this.getSizeTitle_()}">
    <cr-icon slot="icon" icon="${this.getSizeIcon_()}"></cr-icon>
    <ink-size-selector slot="menu" .currentSize="${this.currentSize}"
        .currentType="${this.currentType}"
        @current-size-changed="${this.onCurrentSizeChanged}">
    </ink-size-selector>
  </viewer-bottom-toolbar-dropdown>
  <viewer-bottom-toolbar-dropdown id="color" class="toolbar-icon"
      .buttonTitle="${this.getColorTitle_()}">
    <div slot="icon" class="color-chip"></div>
    <ink-color-selector slot="menu" label="Color"
        .colors="${this.availableBrushColors()}"
        .currentColor="${this.currentColor}"
        @current-color-changed="${this.onCurrentColorChanged}">
    </ink-color-selector>
  </viewer-bottom-toolbar-dropdown>
` : ""}
<!--_html_template_end_-->`
}
const ViewerBottomToolbarElementBase = InkAnnotationBrushMixin(CrLitElement);
class ViewerBottomToolbarElement extends ViewerBottomToolbarElementBase {
    static get is() {
        return "viewer-bottom-toolbar"
    }
    static get styles() {
        return getCss$q()
    }
    render() {
        return getHtml$l.bind(this)()
    }
    static get properties() {
        return {
            strings: {
                type: Object
            }
        }
    }
    #strings_accessor_storage;
    get strings() {
        return this.#strings_accessor_storage
    }
    set strings(value) {
        this.#strings_accessor_storage = value
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("currentColor") && this.currentColor) {
            this.onCurrentColorUpdated_()
        }
    }
    getSizeIcon_() {
        let options;
        switch (this.currentType) {
        case AnnotationBrushType.HIGHLIGHTER:
            options = HIGHLIGHTER_SIZES;
            break;
        case AnnotationBrushType.PEN:
            options = PEN_SIZES;
            break;
        default:
            assertNotReached()
        }
        assert(options);
        const option = options.find((option => option.size === this.currentSize));
        assert(option);
        return "pdf-ink:" + option.icon
    }
    getSizeTitle_() {
        return this.strings ? loadTimeData.getString("ink2Size") : ""
    }
    getColorTitle_() {
        return this.strings ? loadTimeData.getString("ink2Color") : ""
    }
    onCurrentColorUpdated_() {
        assert(this.currentColor);
        const color = this.currentType === AnnotationBrushType.HIGHLIGHTER ? {
            r: blendHighlighterColorValue(this.currentColor.r),
            g: blendHighlighterColorValue(this.currentColor.g),
            b: blendHighlighterColorValue(this.currentColor.b)
        } : this.currentColor;
        this.style.setProperty("--ink-brush-color", colorToHex(color))
    }
    shouldShowBrushOptions_() {
        return this.currentType !== AnnotationBrushType.ERASER
    }
}
customElements.define(ViewerBottomToolbarElement.is, ViewerBottomToolbarElement);
let instance$q = null;
function getCss$p() {
    return instance$q || (instance$q = [...[getCss$E(), getCss$J()], css`#item{align-items:flex-start;cursor:pointer;display:flex;padding:5px 0;position:relative;transition:background-color 100ms ease-out}#item:hover{background-color:var(--cr-menu-background-focus-color)}#item:active{background-color:rgba(255,255,255,0.25)}#title{outline:none;overflow:hidden;text-overflow:ellipsis}#title:focus-visible{outline:auto -webkit-focus-ring-color}#expand-container{--expand-button-size:28px;flex-shrink:0;position:relative;width:var(--expand-button-size)}#expand-container::before{content:'.';visibility:hidden}#expand{--cr-icon-button-fill-color:var(--primary-text-color);--cr-icon-button-icon-size:16px;--cr-icon-button-size:var(--expand-button-size);left:0;margin:0;position:absolute;top:calc((100% - var(--cr-icon-button-size)) / 2);transition:transform 150ms}:host-context([dir=rtl]) #expand{transform:rotate(180deg)}:host([children-shown_]) #expand{transform:rotate(90deg)}`])
}
function getHtml$k() {
    return html`<!--_html_template_start_-->
<div id="item" @click="${this.onClick_}"
    .style="${this.getItemStartPaddingStyle_()}">
  <div id="expand-container">
    <cr-icon-button id="expand" iron-icon="cr:chevron-right"
        ?hidden="${this.getExpandHidden_()}"
        aria-label="Section"
        aria-expanded="${this.childrenShown_}" @click="${this.onExpandClick_}">
    </cr-icon-button>
  </div>
  <span id="title" tabindex="0">${this.bookmark.title}</span>
</div>
${this.childrenShown_ ? html`
  ${this.bookmark.children.map((item => html`
    <viewer-bookmark .bookmark="${item}" .depth="${this.getChildDepth_()}">
    </viewer-bookmark>
  `))}
` : ""}
<!--_html_template_end_-->`
}
const BOOKMARK_INDENT = 20;
var ChangePageOrigin;
(function(ChangePageOrigin) {
    ChangePageOrigin["BOOKMARK"] = "bookmark";
    ChangePageOrigin["THUMBNAIL"] = "thumbnail";
    ChangePageOrigin["PAGE_SELECTOR"] = "pageSelector"
}
)(ChangePageOrigin || (ChangePageOrigin = {}));
class ViewerBookmarkElement extends CrLitElement {
    static get is() {
        return "viewer-bookmark"
    }
    static get styles() {
        return getCss$p()
    }
    render() {
        return getHtml$k.bind(this)()
    }
    static get properties() {
        return {
            bookmark: {
                type: Object
            },
            depth: {
                type: Number
            },
            childrenShown_: {
                type: Boolean,
                reflect: true
            }
        }
    }
    #bookmark_accessor_storage = {
        title: "",
        children: []
    };
    get bookmark() {
        return this.#bookmark_accessor_storage
    }
    set bookmark(value) {
        this.#bookmark_accessor_storage = value
    }
    #depth_accessor_storage = 0;
    get depth() {
        return this.#depth_accessor_storage
    }
    set depth(value) {
        this.#depth_accessor_storage = value
    }
    #childrenShown__accessor_storage = false;
    get childrenShown_() {
        return this.#childrenShown__accessor_storage
    }
    set childrenShown_(value) {
        this.#childrenShown__accessor_storage = value
    }
    firstUpdated() {
        this.$.item.addEventListener("keydown", (e => {
            if (e.key === "Enter") {
                this.onEnter_(e)
            } else if (e.key === " ") {
                this.onSpace_(e)
            }
        }
        ))
    }
    getItemStartPaddingStyle_() {
        return `padding-inline-start: ${this.depth * BOOKMARK_INDENT}px`
    }
    getChildDepth_() {
        return this.depth + 1
    }
    getExpandHidden_() {
        return this.bookmark.children.length <= 0
    }
    onClick_() {
        if (this.bookmark.page != null) {
            if (this.bookmark.zoom != null) {
                this.fire("change-zoom", {
                    zoom: this.bookmark.zoom
                })
            }
            if (this.bookmark.x != null && this.bookmark.y != null) {
                this.fire("change-page-and-xy", {
                    page: this.bookmark.page,
                    x: this.bookmark.x,
                    y: this.bookmark.y,
                    origin: ChangePageOrigin.BOOKMARK
                })
            } else {
                this.fire("change-page", {
                    page: this.bookmark.page,
                    origin: ChangePageOrigin.BOOKMARK
                })
            }
        } else if (this.bookmark.uri != null) {
            this.fire("navigate", {
                uri: this.bookmark.uri,
                newtab: true
            })
        }
    }
    onEnter_(e) {
        if (e.target !== this.$.expand) {
            this.onClick_()
        }
    }
    onSpace_(e) {
        this.onClick_();
        e.preventDefault()
    }
    onExpandClick_(e) {
        this.childrenShown_ = !this.childrenShown_;
        e.stopPropagation()
    }
}
customElements.define(ViewerBookmarkElement.is, ViewerBookmarkElement);
let instance$p = null;
function getCss$o() {
    return instance$p || (instance$p = [...[getCss$E()], css`:host{display:block;padding-inline-end:20px;padding-top:20px}`])
}
function getHtml$j() {
    return html`<!--_html_template_start_-->
${this.bookmarks.map((item => html`
  <viewer-bookmark .bookmark="${item}" depth="0"></viewer-bookmark>
`))}
<!--_html_template_end_-->`
}
class ViewerDocumentOutlineElement extends CrLitElement {
    static get is() {
        return "viewer-document-outline"
    }
    static get styles() {
        return getCss$o()
    }
    render() {
        return getHtml$j.bind(this)()
    }
    static get properties() {
        return {
            bookmarks: {
                type: Array
            }
        }
    }
    #bookmarks_accessor_storage = [];
    get bookmarks() {
        return this.#bookmarks_accessor_storage
    }
    set bookmarks(value) {
        this.#bookmarks_accessor_storage = value
    }
}
customElements.define(ViewerDocumentOutlineElement.is, ViewerDocumentOutlineElement);
function getHtml$i() {
    return html`<!--_html_template_start_-->
<cr-icon-button id="save" iron-icon="cr:download" part="button"
    @click="${this.onSaveClick}" aria-label="Download"
    aria-haspopup="${this.getAriaHasPopup()}" title="Download">
</cr-icon-button>
<cr-action-menu id="menu">
  <button id="save-edited" class="dropdown-item"
      @click="${this.onSaveEditedClick}">
    With your changes
  </button>
  <button id="save-original" class="dropdown-item"
      @click="${this.onSaveOriginalClick}">
    Without your changes
  </button>
</cr-action-menu>
<!--_html_template_end_-->`
}
const SaveRequestType$2 = chrome.pdfViewerPrivate.SaveRequestType;
const ViewerSaveControlsMixin = superClass => {
    class ViewerSaveControlsMixin extends superClass {
        static get properties() {
            return {
                hasEdits: {
                    type: Boolean
                },
                hasInk2Edits: {
                    type: Boolean
                },
                isFormFieldFocused: {
                    type: Boolean
                }
            }
        }
        #hasEdits_accessor_storage = false;
        get hasEdits() {
            return this.#hasEdits_accessor_storage
        }
        set hasEdits(value) {
            this.#hasEdits_accessor_storage = value
        }
        #hasInk2Edits_accessor_storage = false;
        get hasInk2Edits() {
            return this.#hasInk2Edits_accessor_storage
        }
        set hasInk2Edits(value) {
            this.#hasInk2Edits_accessor_storage = value
        }
        #isFormFieldFocused_accessor_storage = false;
        get isFormFieldFocused() {
            return this.#isFormFieldFocused_accessor_storage
        }
        set isFormFieldFocused(value) {
            this.#isFormFieldFocused_accessor_storage = value
        }
        waitForFormFocusChange_ = null;
        updated(changedProperties) {
            super.updated(changedProperties);
            if (changedProperties.has("isFormFieldFocused") && this.waitForFormFocusChange_ !== null) {
                this.waitForFormFocusChange_.resolve(this.hasEdits);
                this.waitForFormFocusChange_ = null
            }
        }
        waitForEdits_() {
            if (this.hasEditsToSave_()) {
                return Promise.resolve(true)
            }
            if (!this.isFormFieldFocused) {
                return Promise.resolve(false)
            }
            this.waitForFormFocusChange_ = new PromiseResolver;
            return this.waitForFormFocusChange_.promise
        }
        getMenu() {
            assertNotReached()
        }
        getSaveButton() {
            assertNotReached()
        }
        getSaveEventType() {
            assertNotReached()
        }
        onSaveClick() {
            this.waitForEdits_().then((hasEdits => {
                if (this.shouldShowSaveMenuOnSaveClick(hasEdits)) {
                    this.showSaveMenu_()
                } else {
                    this.dispatchSaveEvent_(SaveRequestType$2.ORIGINAL)
                }
            }
            ))
        }
        onSaveEditedClick() {
            this.getMenu().close();
            if (this.hasInk2Edits) {
                this.dispatchSaveEvent_(SaveRequestType$2.ANNOTATION);
                return
            }
            this.dispatchSaveEvent_(SaveRequestType$2.EDITED)
        }
        onSaveOriginalClick() {
            this.dispatchSaveEvent_(SaveRequestType$2.ORIGINAL);
            this.getMenu().close()
        }
        shouldShowSaveMenuOnSaveClick(hasEdits) {
            return hasEdits
        }
        dispatchSaveEvent_(type) {
            this.fire(this.getSaveEventType(), type)
        }
        hasEditsToSave_() {
            return this.hasEdits || this.hasInk2Edits
        }
        showSaveMenu_() {
            this.getMenu().showAt(this.getSaveButton(), {
                anchorAlignmentX: AnchorAlignment.CENTER
            });
            this.fire("save-menu-shown-for-testing")
        }
        getAriaHasPopup() {
            return this.hasEditsToSave_() ? "menu" : "false"
        }
    }
    return ViewerSaveControlsMixin
}
;
let instance$o = null;
function getCss$n() {
    return instance$o || (instance$o = [...[], css`:host{display:contents}cr-action-menu::part(dialog){position:fixed;top:48px}:host([menu-open_]) #save{background-color:var(--active-button-bg);border-radius:50%}`])
}
const ViewerDownloadControlsBase = ViewerSaveControlsMixin(CrLitElement);
class ViewerDownloadControlsElement extends ViewerDownloadControlsBase {
    static get is() {
        return "viewer-download-controls"
    }
    static get styles() {
        return [getCss$E(), getCss$n()]
    }
    render() {
        return getHtml$i.bind(this)()
    }
    getSaveButton() {
        return this.$.save
    }
    getSaveEventType() {
        return "save"
    }
    getMenu() {
        return this.$.menu
    }
}
customElements.define(ViewerDownloadControlsElement.is, ViewerDownloadControlsElement);
let instance$n = null;
function getCss$m() {
    return instance$n || (instance$n = [...[], css`#content{align-items:center;color:#fff;direction:ltr;display:flex;font-size:0.81rem;text-align:center;--page-selector-spacing:4px}#pageSelector::selection{background-color:var(--viewer-text-input-selection-color)}input,#pagelength{width:calc(max(2,var(--page-length-digits)) * 1ch + 1px)}input{background:rgba(0,0,0,0.5);border:none;color:white;font-family:inherit;line-height:inherit;outline:none;padding:0 var(--page-selector-spacing);text-align:center}#divider{margin:0 var(--page-selector-spacing)}`])
}
function getHtml$h() {
    return html`<!--_html_template_start_-->
<div id="content">
  <input part="input" type="text" id="pageSelector"
      .value="${this.pageNo.toString()}" @pointerup="${this.onPointerup_}"
      @input="${this.onInput_}" @change="${this.onChange_}"
      aria-label="Page number">
  <span id="divider">/</span>
  <span id="pagelength">${this.docLength}</span>
</div>
<!--_html_template_end_-->`
}
class ViewerPageSelectorElement extends CrLitElement {
    static get is() {
        return "viewer-page-selector"
    }
    static get styles() {
        return getCss$m()
    }
    render() {
        return getHtml$h.bind(this)()
    }
    static get properties() {
        return {
            docLength: {
                type: Number
            },
            pageNo: {
                type: Number
            }
        }
    }
    #docLength_accessor_storage = 1;
    get docLength() {
        return this.#docLength_accessor_storage
    }
    set docLength(value) {
        this.#docLength_accessor_storage = value
    }
    #pageNo_accessor_storage = 1;
    get pageNo() {
        return this.#pageNo_accessor_storage
    }
    set pageNo(value) {
        this.#pageNo_accessor_storage = value
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("docLength")) {
            const numDigits = this.docLength.toString().length;
            this.style.setProperty("--page-length-digits", `${numDigits}`)
        }
    }
    onChange_() {
        const page = parseInt(this.$.pageSelector.value, 10);
        if (!isNaN(page) && page <= this.docLength && page > 0) {
            this.dispatchEvent(new CustomEvent("change-page",{
                detail: {
                    page: page - 1,
                    origin: ChangePageOrigin.PAGE_SELECTOR
                },
                composed: true
            }))
        } else {
            this.$.pageSelector.value = this.pageNo.toString()
        }
        this.$.pageSelector.blur()
    }
    onPointerup_() {
        this.select()
    }
    select() {
        this.$.pageSelector.select()
    }
    isActive() {
        return this.shadowRoot.activeElement === this.$.pageSelector
    }
    onInput_() {
        this.$.pageSelector.value = this.$.pageSelector.value.replace(/[^\d]/, "")
    }
}
customElements.define(ViewerPageSelectorElement.is, ViewerPageSelectorElement);
let instance$m = null;
function getCss$l() {
    return instance$m || (instance$m = [...[getCss$J(), getCss$K()], css`[actionable]{cursor:pointer}.hr{border-top:var(--cr-separator-line)}.cr-separators>*:not([first]){border-top:var(--cr-separator-line)}[scrollable]{border-color:transparent;border-style:solid;border-width:1px 0;overflow-y:auto}[scrollable].is-scrolled{border-top-color:var(--cr-scrollable-border-color)}[scrollable].can-scroll:not(.scrolled-to-bottom){border-bottom-color:var(--cr-scrollable-border-color)}[scrollable] iron-list>:not(.no-outline):focus-visible,[selectable]:focus-visible,[selectable]>:focus-visible{outline:solid 2px var(--cr-focus-outline-color);outline-offset:-2px}.scroll-container{display:flex;flex-direction:column;min-height:1px}[selectable]>*{cursor:pointer}.cr-centered-card-container{box-sizing:border-box;display:block;height:inherit;margin:0 auto;max-width:var(--cr-centered-card-max-width);min-width:550px;position:relative;width:calc(100% * var(--cr-centered-card-width-percentage))}.cr-row{align-items:center;border-top:var(--cr-separator-line);display:flex;min-height:var(--cr-section-min-height);padding:0 var(--cr-section-padding)}.cr-row.first,.cr-row.continuation{border-top:none}.cr-row-gap{padding-inline-start:16px}.cr-button-gap{margin-inline-start:8px}paper-tooltip::part(tooltip),cr-tooltip::part(tooltip){border-radius:var(--paper-tooltip-border-radius,2px);font-size:92.31%;font-weight:500;max-width:330px;min-width:var(--paper-tooltip-min-width,200px);padding:var(--paper-tooltip-padding,10px 8px)}.cr-padded-text{padding-block-end:var(--cr-section-vertical-padding);padding-block-start:var(--cr-section-vertical-padding)}.cr-title-text{color:var(--cr-title-text-color);font-size:107.6923%;font-weight:500}.cr-secondary-text{color:var(--cr-secondary-text-color);font-weight:400}.cr-form-field-label{color:var(--cr-form-field-label-color);display:block;font-size:var(--cr-form-field-label-font-size);font-weight:500;letter-spacing:.4px;line-height:var(--cr-form-field-label-line-height);margin-bottom:8px}.cr-vertical-tab{align-items:center;display:flex}.cr-vertical-tab::before{border-radius:0 3px 3px 0;content:'';display:block;flex-shrink:0;height:var(--cr-vertical-tab-height,100%);width:4px}.cr-vertical-tab.selected::before{background:var(--cr-vertical-tab-selected-color,var(--cr-checked-color))}:host-context([dir=rtl]) .cr-vertical-tab::before{transform:scaleX(-1)}.iph-anchor-highlight{background-color:var(--cr-iph-anchor-highlight-color)}`])
}
let instance$l = null;
function getCss$k() {
    return instance$l || (instance$l = [...[], css`:host{--cr-input-background-color:var(--color-textfield-filled-background,var(--cr-fallback-color-surface-variant));--cr-input-border-bottom:1px solid var(--color-textfield-filled-underline,var(--cr-fallback-color-outline));--cr-input-border-radius:8px 8px 0 0;--cr-input-color:var(--cr-primary-text-color);--cr-input-error-color:var(--color-textfield-filled-error,var(--cr-fallback-color-error));--cr-input-focus-color:var(--color-textfield-filled-underline-focused,var(--cr-fallback-color-primary));--cr-input-hover-background-color:var(--cr-hover-background-color);--cr-input-label-color:var(--color-textfield-foreground-label,var(--cr-fallback-color-on-surface-subtle));--cr-input-padding-bottom:10px;--cr-input-padding-end:10px;--cr-input-padding-start:10px;--cr-input-padding-top:10px;--cr-input-placeholder-color:var(--color-textfield-foreground-placeholder,var(--cr-fallback-on-surface-subtle));display:block;isolation:isolate;outline:none}:host([readonly]){--cr-input-border-radius:8px 8px}#label{color:var(--cr-input-label-color);font-size:11px;line-height:16px}:host([focused_]:not([readonly]):not([invalid])) #label{color:var(--cr-input-focus-label-color,var(--cr-input-label-color))}#input-container{border-radius:var(--cr-input-border-radius,4px);overflow:hidden;position:relative;width:var(--cr-input-width,100%)}:host([focused_]) #input-container{outline:var(--cr-input-focus-outline,none)}#inner-input-container{background-color:var(--cr-input-background-color);box-sizing:border-box;padding:0}#inner-input-content ::slotted(*){--cr-icon-button-fill-color:var(--color-textfield-foreground-icon,var(--cr-fallback-color-on-surface-subtle));--cr-icon-button-icon-size:16px;--cr-icon-button-size:24px;--cr-icon-button-margin-start:0;--cr-icon-color:var(--color-textfield-foreground-icon,var(--cr-fallback-color-on-surface-subtle))}#inner-input-content ::slotted([slot='inline-prefix']){--cr-icon-button-margin-start:-8px}#inner-input-content ::slotted([slot='inline-suffix']){--cr-icon-button-margin-end:-4px}:host([invalid]) #inner-input-content ::slotted(*){--cr-icon-color:var(--cr-input-error-color);--cr-icon-button-fill-color:var(--cr-input-error-color)}#hover-layer{background-color:var(--cr-input-hover-background-color);display:none;inset:0;pointer-events:none;position:absolute;z-index:0}:host(:not([readonly]):not([disabled])) #input-container:hover #hover-layer{display:block}#input{-webkit-appearance:none;background-color:transparent;border:none;box-sizing:border-box;caret-color:var(--cr-input-focus-color);color:var(--cr-input-color);font-family:inherit;font-size:var(--cr-input-font-size,12px);font-weight:inherit;line-height:16px;min-height:var(--cr-input-min-height,auto);outline:none;padding:0;text-align:inherit;text-overflow:ellipsis;width:100%}#inner-input-content{padding-bottom:var(--cr-input-padding-bottom);padding-inline-end:var(--cr-input-padding-end);padding-inline-start:var(--cr-input-padding-start);padding-top:var(--cr-input-padding-top)}#underline{border-bottom:2px solid var(--cr-input-focus-color);border-radius:var(--cr-input-underline-border-radius,0);bottom:0;box-sizing:border-box;display:var(--cr-input-underline-display);height:var(--cr-input-underline-height,0);left:0;margin:auto;opacity:0;position:absolute;right:0;transition:opacity 120ms ease-out,width 0s linear 180ms;width:0}:host([invalid]) #underline,:host([force-underline]) #underline,:host([focused_]) #underline{opacity:1;transition:opacity 120ms ease-in,width 180ms ease-out;width:100%}#underline-base{display:none}:host([readonly]) #underline{display:none}:host(:not([readonly])) #underline-base{border-bottom:var(--cr-input-border-bottom);bottom:0;display:block;left:0;position:absolute;right:0}:host([disabled]){color:var(--color-textfield-foreground-disabled,var(--cr-fallback-color-disabled-foreground));--cr-input-border-bottom:1px solid currentColor;--cr-input-placeholder-color:currentColor;--cr-input-color:currentColor;--cr-input-background-color:var(--color-textfield-background-disabled,var(--cr-fallback-color-disabled-background))}:host([disabled]) #inner-input-content ::slotted(*){--cr-icon-color:currentColor;--cr-icon-button-fill-color:currentColor}:host(.stroked){--cr-input-background-color:transparent;--cr-input-border:1px solid var(--color-side-panel-textfield-border,var(--cr-fallback-color-neutral-outline));--cr-input-border-bottom:none;--cr-input-border-radius:8px;--cr-input-padding-bottom:9px;--cr-input-padding-end:9px;--cr-input-padding-start:9px;--cr-input-padding-top:9px;--cr-input-underline-display:none;--cr-input-min-height:36px;line-height:16px}:host(.stroked[focused_]){--cr-input-border:2px solid var(--cr-focus-outline-color);--cr-input-padding-bottom:8px;--cr-input-padding-end:8px;--cr-input-padding-start:8px;--cr-input-padding-top:8px}:host(.stroked[invalid]){--cr-input-border:1px solid var(--cr-input-error-color)}:host(.stroked[focused_][invalid]){--cr-input-border:2px solid var(--cr-input-error-color)}`])
}
let instance$k = null;
function getCss$j() {
    return instance$k || (instance$k = [...[getCss$J(), getCss$k(), getCss$l()], css`:host([disabled]) :-webkit-any(#label,#error,#input-container){opacity:var(--cr-disabled-opacity);pointer-events:none}:host([disabled]) :is(#label,#error,#input-container){opacity:1}:host ::slotted(cr-button[slot=suffix]){margin-inline-start:var(--cr-button-edge-spacing) !important}:host([invalid]) #label{color:var(--cr-input-error-color)}#input{border-bottom:none;letter-spacing:var(--cr-input-letter-spacing)}#input-container{border:var(--cr-input-border,none)}#input::placeholder{color:var(--cr-input-placeholder-color,var(--cr-secondary-text-color));letter-spacing:var(--cr-input-placeholder-letter-spacing)}:host([invalid]) #input{caret-color:var(--cr-input-error-color)}:host([readonly]) #input{opacity:var(--cr-input-readonly-opacity,0.6)}:host([invalid]) #underline{border-color:var(--cr-input-error-color)}#error{color:var(--cr-input-error-color);display:var(--cr-input-error-display,block);font-size:11px;min-height:var(--cr-form-field-label-height);line-height:16px;margin:4px 10px;visibility:hidden;white-space:var(--cr-input-error-white-space);height:auto;overflow:hidden;text-overflow:ellipsis}:host([invalid]) #error{visibility:visible}#row-container,#inner-input-content{align-items:center;display:flex;justify-content:space-between;position:relative}#inner-input-content{gap:4px;height:16px;z-index:1}#input[type='search']::-webkit-search-cancel-button{display:none}:host-context([dir=rtl]) #input[type=url]{text-align:right}#input[type=url]{direction:ltr}`])
}
function getHtml$g() {
    return html`
<div id="label" class="cr-form-field-label" ?hidden="${!this.label}"
    aria-hidden="${this.getLabelAriaHidden_() || nothing}">
  ${this.label}
</div>
<div id="row-container" part="row-container">
  <div id="input-container">
    <div id="inner-input-container">
      <div id="hover-layer"></div>
      <div id="inner-input-content">
        <slot name="inline-prefix"></slot>
        <input id="input" ?disabled="${this.disabled}"
            ?autofocus="${this.autofocus}" .value="${this.internalValue_}"
            tabindex="${this.inputTabindex}" .type="${this.type}"
            ?readonly="${this.readonly}" maxlength="${this.maxlength}"
            pattern="${this.pattern || nothing}" ?required="${this.required}"
            minlength="${this.minlength}" inputmode="${this.inputmode}"
            aria-description="${this.ariaDescription || nothing}"
            aria-errormessage="${this.getAriaErrorMessage_() || nothing}"
            aria-labelledby="${this.getAriaLabelledBy_() || nothing}"
            aria-label="${this.getAriaLabel_()}"
            aria-invalid="${this.getAriaInvalid_()}"
            .max="${this.max || nothing}" .min="${this.min || nothing}"
            @focus="${this.onInputFocus_}" @blur="${this.onInputBlur_}"
            @change="${this.onInputChange_}" @input="${this.onInput_}"
            part="input" autocomplete="off">
        <slot name="inline-suffix"></slot>
      </div>
    </div>
    <div id="underline-base"></div>
    <div id="underline"></div>
  </div>
  <slot name="suffix"></slot>
</div>
<div id="error" role="${this.getErrorRole_() || nothing}"
    aria-live="assertive">${this.getErrorMessage_()}</div>`
}
const SUPPORTED_INPUT_TYPES = new Set(["number", "password", "search", "text", "url"]);
class CrInputElement extends CrLitElement {
    static get is() {
        return "cr-input"
    }
    static get styles() {
        return getCss$j()
    }
    render() {
        return getHtml$g.bind(this)()
    }
    static get properties() {
        return {
            ariaDescription: {
                type: String
            },
            ariaLabel: {
                type: String
            },
            autofocus: {
                type: Boolean,
                reflect: true
            },
            autoValidate: {
                type: Boolean
            },
            disabled: {
                type: Boolean,
                reflect: true
            },
            errorMessage: {
                type: String
            },
            focused_: {
                type: Boolean,
                reflect: true
            },
            invalid: {
                type: Boolean,
                notify: true,
                reflect: true
            },
            max: {
                type: Number,
                reflect: true
            },
            min: {
                type: Number,
                reflect: true
            },
            maxlength: {
                type: Number,
                reflect: true
            },
            minlength: {
                type: Number,
                reflect: true
            },
            pattern: {
                type: String,
                reflect: true
            },
            inputmode: {
                type: String
            },
            label: {
                type: String
            },
            placeholder: {
                type: String
            },
            readonly: {
                type: Boolean,
                reflect: true
            },
            required: {
                type: Boolean,
                reflect: true
            },
            inputTabindex: {
                type: Number
            },
            type: {
                type: String
            },
            value: {
                type: String,
                notify: true
            },
            internalValue_: {
                type: String,
                state: true
            }
        }
    }
    #ariaDescription_accessor_storage = null;
    get ariaDescription() {
        return this.#ariaDescription_accessor_storage
    }
    set ariaDescription(value) {
        this.#ariaDescription_accessor_storage = value
    }
    #ariaLabel_accessor_storage = "";
    get ariaLabel() {
        return this.#ariaLabel_accessor_storage
    }
    set ariaLabel(value) {
        this.#ariaLabel_accessor_storage = value
    }
    #autofocus_accessor_storage = false;
    get autofocus() {
        return this.#autofocus_accessor_storage
    }
    set autofocus(value) {
        this.#autofocus_accessor_storage = value
    }
    #autoValidate_accessor_storage = false;
    get autoValidate() {
        return this.#autoValidate_accessor_storage
    }
    set autoValidate(value) {
        this.#autoValidate_accessor_storage = value
    }
    #disabled_accessor_storage = false;
    get disabled() {
        return this.#disabled_accessor_storage
    }
    set disabled(value) {
        this.#disabled_accessor_storage = value
    }
    #errorMessage_accessor_storage = "";
    get errorMessage() {
        return this.#errorMessage_accessor_storage
    }
    set errorMessage(value) {
        this.#errorMessage_accessor_storage = value
    }
    #inputmode_accessor_storage;
    get inputmode() {
        return this.#inputmode_accessor_storage
    }
    set inputmode(value) {
        this.#inputmode_accessor_storage = value
    }
    #inputTabindex_accessor_storage = 0;
    get inputTabindex() {
        return this.#inputTabindex_accessor_storage
    }
    set inputTabindex(value) {
        this.#inputTabindex_accessor_storage = value
    }
    #invalid_accessor_storage = false;
    get invalid() {
        return this.#invalid_accessor_storage
    }
    set invalid(value) {
        this.#invalid_accessor_storage = value
    }
    #label_accessor_storage = "";
    get label() {
        return this.#label_accessor_storage
    }
    set label(value) {
        this.#label_accessor_storage = value
    }
    #max_accessor_storage;
    get max() {
        return this.#max_accessor_storage
    }
    set max(value) {
        this.#max_accessor_storage = value
    }
    #min_accessor_storage;
    get min() {
        return this.#min_accessor_storage
    }
    set min(value) {
        this.#min_accessor_storage = value
    }
    #maxlength_accessor_storage;
    get maxlength() {
        return this.#maxlength_accessor_storage
    }
    set maxlength(value) {
        this.#maxlength_accessor_storage = value
    }
    #minlength_accessor_storage;
    get minlength() {
        return this.#minlength_accessor_storage
    }
    set minlength(value) {
        this.#minlength_accessor_storage = value
    }
    #pattern_accessor_storage;
    get pattern() {
        return this.#pattern_accessor_storage
    }
    set pattern(value) {
        this.#pattern_accessor_storage = value
    }
    #placeholder_accessor_storage = null;
    get placeholder() {
        return this.#placeholder_accessor_storage
    }
    set placeholder(value) {
        this.#placeholder_accessor_storage = value
    }
    #readonly_accessor_storage = false;
    get readonly() {
        return this.#readonly_accessor_storage
    }
    set readonly(value) {
        this.#readonly_accessor_storage = value
    }
    #required_accessor_storage = false;
    get required() {
        return this.#required_accessor_storage
    }
    set required(value) {
        this.#required_accessor_storage = value
    }
    #type_accessor_storage = "text";
    get type() {
        return this.#type_accessor_storage
    }
    set type(value) {
        this.#type_accessor_storage = value
    }
    #value_accessor_storage = "";
    get value() {
        return this.#value_accessor_storage
    }
    set value(value) {
        this.#value_accessor_storage = value
    }
    #internalValue__accessor_storage = "";
    get internalValue_() {
        return this.#internalValue__accessor_storage
    }
    set internalValue_(value) {
        this.#internalValue__accessor_storage = value
    }
    #focused__accessor_storage = false;
    get focused_() {
        return this.#focused__accessor_storage
    }
    set focused_(value) {
        this.#focused__accessor_storage = value
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("value")) {
            this.internalValue_ = this.value === undefined || this.value === null ? "" : this.value
        }
        if (changedProperties.has("inputTabindex")) {
            assert(this.inputTabindex === 0 || this.inputTabindex === -1)
        }
        if (changedProperties.has("type")) {
            assert(SUPPORTED_INPUT_TYPES.has(this.type))
        }
    }
    firstUpdated() {
        assert(!this.hasAttribute("tabindex"))
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("value")) {
            const previous = changedProperties.get("value");
            if ((!!this.value || !!previous) && this.autoValidate) {
                this.invalid = !this.inputElement.checkValidity()
            }
        }
        if (changedProperties.has("placeholder")) {
            if (this.placeholder === null || this.placeholder === undefined) {
                this.inputElement.removeAttribute("placeholder")
            } else {
                this.inputElement.setAttribute("placeholder", this.placeholder)
            }
        }
    }
    get inputElement() {
        return this.$.input
    }
    focus() {
        this.focusInput()
    }
    focusInput() {
        if (this.shadowRoot.activeElement === this.inputElement) {
            return false
        }
        this.inputElement.focus();
        return true
    }
    async onInputChange_(e) {
        await this.updateComplete;
        this.fire("change", {
            sourceEvent: e
        })
    }
    onInput_(e) {
        this.internalValue_ = e.target.value;
        this.value = this.internalValue_
    }
    onInputFocus_() {
        this.focused_ = true
    }
    onInputBlur_() {
        this.focused_ = false
    }
    getAriaLabel_() {
        return this.ariaLabel || this.label || this.placeholder
    }
    getAriaLabelledBy_() {
        if (this.label && !this.ariaLabel) {
            return "label"
        }
        return null
    }
    getLabelAriaHidden_() {
        return this.getAriaLabelledBy_() ? null : "true"
    }
    getAriaInvalid_() {
        return this.invalid ? "true" : "false"
    }
    getErrorMessage_() {
        return this.invalid ? this.errorMessage : ""
    }
    getErrorRole_() {
        return this.invalid ? "alert" : ""
    }
    getAriaErrorMessage_() {
        return this.invalid ? "error" : ""
    }
    select(start, end) {
        this.inputElement.focus();
        if (start !== undefined && end !== undefined) {
            this.inputElement.setSelectionRange(start, end)
        } else {
            assert(start === undefined && end === undefined);
            this.inputElement.select()
        }
    }
    validate() {
        this.performUpdate();
        this.invalid = !this.inputElement.checkValidity();
        this.performUpdate();
        return !this.invalid
    }
}
customElements.define(CrInputElement.is, CrInputElement);
let instance$j = null;
function getCss$i() {
    return instance$j || (instance$j = [...[getCss$l()], css`#password{margin-top:var(--cr-form-field-bottom-spacing)}`])
}
function getHtml$f() {
    return html`<!--_html_template_start_-->
<cr-dialog id="dialog" no-cancel show-on-attach>
  <div slot="title">Password required</div>
  <div slot="body">
    <div id="message">This document is password protected.  Please enter a password.</div>
    <cr-input id="password" type="password"
        error-message="Incorrect password" .invalid="${this.invalid}"
        autofocus>
    </cr-input>
  </div>
  <div slot="button-container">
    <cr-button id="submit" class="action-button"
        @click="${this.onSubmitClick_}">
      Submit
    </cr-button>
  </div>
</cr-dialog>
<!--_html_template_end_-->`
}
class ViewerPasswordDialogElement extends CrLitElement {
    static get is() {
        return "viewer-password-dialog"
    }
    static get styles() {
        return getCss$i()
    }
    render() {
        return getHtml$f.bind(this)()
    }
    static get properties() {
        return {
            invalid: {
                type: Boolean
            }
        }
    }
    #invalid_accessor_storage = false;
    get invalid() {
        return this.#invalid_accessor_storage
    }
    set invalid(value) {
        this.#invalid_accessor_storage = value
    }
    close() {
        this.$.dialog.close()
    }
    deny() {
        const password = this.$.password;
        password.disabled = false;
        this.$.submit.disabled = false;
        this.invalid = true;
        password.select();
        this.dispatchEvent(new CustomEvent("password-denied-for-testing"))
    }
    onSubmitClick_() {
        const password = this.$.password;
        if (password.value.length === 0) {
            return
        }
        password.disabled = true;
        this.$.submit.disabled = true;
        this.dispatchEvent(new CustomEvent("password-submitted",{
            detail: {
                password: password.value
            }
        }))
    }
}
customElements.define(ViewerPasswordDialogElement.is, ViewerPasswordDialogElement);
let instance$i = null;
function getCss$h() {
    return instance$i || (instance$i = [...[getCss$E()], css`:host{--focus-border-color:var(--google-blue-300);display:block}:host(:focus){outline:none}#thumbnail{align-items:center;background-color:white;cursor:pointer;display:inline-flex;height:140px;justify-content:center;margin-bottom:12px;margin-inline-end:auto;margin-inline-start:auto;width:108px}:host([is-active]) #thumbnail{box-shadow:0 0 0 6px var(--focus-border-color)}:host(:focus-visible) #thumbnail{box-shadow:0 0 0 2px var(--focus-border-color)}:host([is-active]:focus-visible) #thumbnail{box-shadow:0 0 0 8px var(--focus-border-color)}canvas{display:block;opacity:0.5}:host([is-active]) canvas{opacity:1}:host([is-active]) canvas:hover,canvas:hover{opacity:0.7}#pageNumber{line-height:1}`])
}
function getHtml$e() {
    return html`
<div id="thumbnail" @click="${this.onClick_}" role="button"></div>
<div id="pageNumber">${this.pageNumber}</div>`
}
const PORTRAIT_WIDTH = 108;
const LANDSCAPE_WIDTH = 140;
const PAINTED_ATTRIBUTE = "painted";
class ViewerThumbnailElement extends CrLitElement {
    static get is() {
        return "viewer-thumbnail"
    }
    static get styles() {
        return getCss$h()
    }
    render() {
        return getHtml$e.bind(this)()
    }
    static get properties() {
        return {
            clockwiseRotations: {
                type: Number
            },
            isActive: {
                type: Boolean,
                reflect: true
            },
            pageNumber: {
                type: Number
            }
        }
    }
    #clockwiseRotations_accessor_storage = 0;
    get clockwiseRotations() {
        return this.#clockwiseRotations_accessor_storage
    }
    set clockwiseRotations(value) {
        this.#clockwiseRotations_accessor_storage = value
    }
    #isActive_accessor_storage = true;
    get isActive() {
        return this.#isActive_accessor_storage
    }
    set isActive(value) {
        this.#isActive_accessor_storage = value
    }
    #pageNumber_accessor_storage = 0;
    get pageNumber() {
        return this.#pageNumber_accessor_storage
    }
    set pageNumber(value) {
        this.#pageNumber_accessor_storage = value
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("clockwiseRotations")) {
            this.styleCanvas_()
        }
        if (changedProperties.has("isActive") && this.isActive) {
            const scrollIntoViewOptions = {
                block: "nearest"
            };
            if (document.documentElement.hasAttribute("pdfOopifEnabled")) {
                scrollIntoViewOptions.container = "nearest"
            }
            this.scrollIntoView(scrollIntoViewOptions)
        }
    }
    set image(imageData) {
        let canvas = this.getCanvas_();
        if (!canvas) {
            canvas = document.createElement("canvas");
            canvas.oncontextmenu = e => e.preventDefault();
            this.$.thumbnail.appendChild(canvas)
        }
        canvas.width = imageData.width;
        canvas.height = imageData.height;
        this.styleCanvas_();
        const ctx = canvas.getContext("2d");
        ctx.putImageData(imageData, 0, 0)
    }
    clearImage() {
        if (!this.isPainted()) {
            return
        }
        const canvas = this.getCanvas_();
        if (canvas) {
            canvas.remove()
        }
        this.removeAttribute(PAINTED_ATTRIBUTE)
    }
    getClickTarget() {
        return this.$.thumbnail
    }
    getCanvas_() {
        return this.shadowRoot.querySelector("canvas")
    }
    getThumbnailCssSize_(rotated) {
        const canvas = this.getCanvas_();
        const isPortrait = canvas.width !== canvas.height && canvas.width < canvas.height !== rotated;
        const orientedWidth = rotated ? canvas.height : canvas.width;
        const orientedHeight = rotated ? canvas.width : canvas.height;
        const cssWidth = Math.min(isPortrait ? PORTRAIT_WIDTH : LANDSCAPE_WIDTH, Math.trunc(orientedWidth / window.devicePixelRatio));
        const scale = cssWidth / orientedWidth;
        const cssHeight = Math.trunc(orientedHeight * scale);
        return {
            width: cssWidth,
            height: cssHeight
        }
    }
    focusAndScroll() {
        this.scrollIntoView({
            block: "nearest"
        });
        this.focus({
            preventScroll: true
        })
    }
    isPainted() {
        return this.hasAttribute(PAINTED_ATTRIBUTE)
    }
    setPainted() {
        this.toggleAttribute(PAINTED_ATTRIBUTE, true)
    }
    onClick_() {
        this.fire("change-page", {
            page: this.pageNumber - 1,
            origin: ChangePageOrigin.THUMBNAIL
        })
    }
    styleCanvas_() {
        assert(this.clockwiseRotations >= 0 && this.clockwiseRotations < 4);
        const canvas = this.getCanvas_();
        if (!canvas) {
            return
        }
        const div = this.shadowRoot.querySelector("#thumbnail");
        const degreesRotated = this.clockwiseRotations * 90;
        canvas.style.transform = `rotate(${degreesRotated}deg)`;
        const rotated = this.clockwiseRotations % 2 !== 0;
        const cssSize = this.getThumbnailCssSize_(rotated);
        div.style.width = `${cssSize.width}px`;
        div.style.height = `${cssSize.height}px`;
        canvas.style.width = `${rotated ? cssSize.height : cssSize.width}px`;
        canvas.style.height = `${rotated ? cssSize.width : cssSize.height}px`
    }
}
customElements.define(ViewerThumbnailElement.is, ViewerThumbnailElement);
let instance$h = null;
function getCss$g() {
    return instance$h || (instance$h = [...[], css`:host(:focus){outline:none}#thumbnails{box-sizing:border-box;height:100%;overflow:auto;padding-bottom:24px;padding-inline-end:var(--viewer-thumbnail-bar-padding-inline-end);text-align:center}viewer-thumbnail{padding-top:24px}`])
}
function getHtml$d() {
    return html`
<div id="thumbnails" ?hidden="${!this.isPluginActive_}" role="tablist">
  ${this.computePageNumbers_().map((item => html`
    <viewer-thumbnail tabindex="0" role="tab"
        aria-label="${this.getAriaLabel_(item)}"
        aria-selected="${this.isActivePage_(item)}"
        .clockwiseRotations="${this.clockwiseRotations}"
        .isActive="${this.isActivePage_(item)}" .pageNumber="${item}">
    </viewer-thumbnail>
  `))}
</div>`
}
const DEBOUNCE_DELAY_MS = 100;
class ViewerThumbnailBarElement extends CrLitElement {
    static get is() {
        return "viewer-thumbnail-bar"
    }
    static get styles() {
        return getCss$g()
    }
    render() {
        return getHtml$d.bind(this)()
    }
    static get properties() {
        return {
            activePage: {
                type: Number
            },
            clockwiseRotations: {
                type: Number
            },
            docLength: {
                type: Number
            },
            isPluginActive_: {
                type: Boolean
            }
        }
    }
    #activePage_accessor_storage = 0;
    get activePage() {
        return this.#activePage_accessor_storage
    }
    set activePage(value) {
        this.#activePage_accessor_storage = value
    }
    #clockwiseRotations_accessor_storage = 0;
    get clockwiseRotations() {
        return this.#clockwiseRotations_accessor_storage
    }
    set clockwiseRotations(value) {
        this.#clockwiseRotations_accessor_storage = value
    }
    #docLength_accessor_storage = 0;
    get docLength() {
        return this.#docLength_accessor_storage
    }
    set docLength(value) {
        this.#docLength_accessor_storage = value
    }
    #isPluginActive__accessor_storage = false;
    get isPluginActive_() {
        return this.#isPluginActive__accessor_storage
    }
    set isPluginActive_(value) {
        this.#isPluginActive__accessor_storage = value
    }
    intersectionObserver_ = null;
    pendingThumbnails_ = new Map;
    pluginController_ = PluginController.getInstance();
    processPendingThumbnailsDebounced_ = debounceEnd(( () => this.processPendingThumbnails_()), DEBOUNCE_DELAY_MS);
    tracker_ = new EventTracker;
    constructor() {
        super();
        this.isPluginActive_ = this.pluginController_.isActive;
        this.tracker_.add(this.pluginController_.getEventTarget(), PluginControllerEventType.IS_ACTIVE_CHANGED, (e => {
            this.isPluginActive_ = e.detail;
            if (!this.isPluginActive_) {
                this.pendingThumbnails_.clear()
            }
        }
        ));
        this.tracker_.add(this.pluginController_.getEventTarget(), PluginControllerEventType.UPDATE_THUMBNAIL, this.handleUpdateThumbnail_.bind(this))
    }
    firstUpdated() {
        this.addEventListener("focus", this.onFocus_);
        this.addEventListener("keydown", this.onKeydown_);
        const thumbnailsDiv = this.$.thumbnails;
        this.intersectionObserver_ = new IntersectionObserver((entries => {
            entries.forEach((entry => {
                const thumbnail = entry.target;
                const pageIndex = thumbnail.pageNumber - 1;
                if (!entry.isIntersecting) {
                    this.pendingThumbnails_.delete(pageIndex);
                    thumbnail.clearImage();
                    return
                }
                if (thumbnail.isPainted()) {
                    return
                }
                thumbnail.setPainted();
                if (!this.isPluginActive_) {
                    return
                }
                this.pendingThumbnails_.set(pageIndex, thumbnail);
                this.processPendingThumbnailsDebounced_()
            }
            ))
        }
        ),{
            root: thumbnailsDiv,
            rootMargin: "500% 0% 100%"
        });
        FocusOutlineManager.forDocument(document)
    }
    processPendingThumbnails_() {
        if (!this.isPluginActive_) {
            this.pendingThumbnails_.clear();
            return
        }
        const queue = Array.from(this.pendingThumbnails_.entries()).filter(( ([_,thumbnail]) => thumbnail.isPainted()));
        this.pendingThumbnails_.clear();
        for (const [pageIndex,thumbnail] of queue) {
            this.pluginController_.requestThumbnail(pageIndex).then((response => {
                if (thumbnail.isPainted()) {
                    const array = new Uint8ClampedArray(response.imageData);
                    const imageData = new ImageData(array,response.width);
                    thumbnail.image = imageData
                }
            }
            ))
        }
        this.dispatchEvent(new CustomEvent("thumbnails-processed-for-testing"))
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("activePage")) {
            if (this.shadowRoot.activeElement) {
                this.getThumbnailForPage(this.activePage).focusAndScroll()
            }
        }
        if (changedProperties.has("docLength")) {
            assert(this.intersectionObserver_);
            this.shadowRoot.querySelectorAll("viewer-thumbnail").forEach((thumbnail => this.intersectionObserver_.observe(thumbnail)))
        }
    }
    clickThumbnailForPage(pageNumber) {
        const thumbnail = this.getThumbnailForPage(pageNumber);
        if (!thumbnail) {
            return
        }
        thumbnail.getClickTarget().click()
    }
    getThumbnailForPage(pageNumber) {
        return this.shadowRoot.querySelector(`viewer-thumbnail:nth-child(${pageNumber})`)
    }
    computePageNumbers_() {
        return Array.from({
            length: this.docLength
        }, ( (_, i) => i + 1))
    }
    getAriaLabel_(pageNumber) {
        return loadTimeData.getStringF("thumbnailPageAriaLabel", pageNumber)
    }
    isActivePage_(page) {
        return this.activePage === page
    }
    onFocus_() {
        const focusOutlineManager = FocusOutlineManager.forDocument(document);
        if (!focusOutlineManager.visible) {
            return
        }
        const activeThumbnail = this.shadowRoot.querySelector("viewer-thumbnail[is-active]");
        if (activeThumbnail) {
            activeThumbnail.focus();
            return
        }
        const firstThumbnail = this.shadowRoot.querySelector("viewer-thumbnail");
        if (!firstThumbnail) {
            return
        }
        firstThumbnail.focus()
    }
    onKeydown_(e) {
        switch (e.key) {
        case "Tab":
            if (e.shiftKey) {
                this.focus();
                return
            }
            const lastThumbnail = this.shadowRoot.querySelector("viewer-thumbnail:last-of-type");
            assert(lastThumbnail);
            lastThumbnail.focus({
                preventScroll: true
            });
            break;
        case "ArrowRight":
        case "ArrowDown":
            e.preventDefault();
            this.clickThumbnailForPage(this.activePage + 1);
            break;
        case "ArrowLeft":
        case "ArrowUp":
            e.preventDefault();
            this.clickThumbnailForPage(this.activePage - 1);
            break
        }
    }
    handleUpdateThumbnail_(e) {
        const data = e.detail;
        const thumbnail = this.getThumbnailForPage(data.pageNumber);
        if (thumbnail && thumbnail.isPainted()) {
            const array = new Uint8ClampedArray(data.imageData);
            thumbnail.image = new ImageData(array,data.width)
        }
    }
}
customElements.define(ViewerThumbnailBarElement.is, ViewerThumbnailBarElement);
let instance$g = null;
function getCss$f() {
    return instance$g || (instance$g = [...[getCss$E(), getCss$J(), getCss$l()], css`:host{--sidenav-selected-tab-color:var(--google-blue-300);background-color:var(--viewer-side-background-color);display:flex;height:100%;min-width:var(--viewer-pdf-sidenav-width);overflow:hidden;width:var(--viewer-pdf-sidenav-width)}#icons{display:flex;flex-direction:column;min-width:64px}#content{color:white;flex:1;overflow-x:hidden}#icons:not([hidden])+#content{--viewer-thumbnail-bar-padding-inline-end:28px}.selected cr-icon-button{--cr-icon-button-fill-color:var(--sidenav-selected-tab-color)}.button-wrapper{--button-wrapper-height:36px;--button-wrapper-margin:12px;--button-wrapper-total-height:calc(var(--button-wrapper-height) + var(--button-wrapper-margin));align-items:center;display:flex;height:var(--button-wrapper-height);margin:var(--button-wrapper-margin) 0;width:100%}.cr-vertical-tab{--cr-vertical-tab-selected-color:var(--sidenav-selected-tab-color)}.cr-vertical-tab::before{transform:translateY(var(--button-wrapper-total-height));transition:transform 250ms cubic-bezier(.4,0,.2,1)}.cr-vertical-tab.selected+.cr-vertical-tab::before{transform:translateY(calc(-1 * var(--button-wrapper-total-height)))}.cr-vertical-tab.selected::before{transform:translateY(0)}cr-icon-button{margin:0 auto}`])
}
function getHtml$c() {
    return html`
<div id="icons" ?hidden="${this.hideIcons_()}" role="tablist"
    @keydown="${this.onKeydown_}">
  ${this.tabs_.map((item => html`
    <div
        class="button-wrapper cr-vertical-tab
        ${this.getTabSelectedClass_(item.id)}">
      <cr-icon-button .ironIcon="${item.icon}" role="tab" title="${item.title}"
          data-tab-id="${item.id}"
          aria-selected="${this.getTabAriaSelected_(item.id)}"
          tabindex="${this.getTabIndex_(item.id)}" @click="${this.onTabClick_}">
      </cr-icon-button>
    </div>
  `))}
</div>
<div id="content">
  <viewer-thumbnail-bar id="thumbnail-bar" tabindex="0"
      ?hidden="${this.hideThumbnailView_()}" .activePage="${this.activePage}"
      .clockwiseRotations="${this.clockwiseRotations}"
      .docLength="${this.docLength}">
  </viewer-thumbnail-bar>
  <viewer-document-outline id="outline" ?hidden="${this.hideOutlineView_()}"
      .bookmarks="${this.bookmarks}">
  </viewer-document-outline>
  <viewer-attachment-bar id="attachment-bar"
      ?hidden="${this.hideAttachmentView_()}"
      .attachments="${this.attachments}">
  </viewer-attachment-bar>
</div>`
}
var TabId;
(function(TabId) {
    TabId[TabId["THUMBNAIL"] = 0] = "THUMBNAIL";
    TabId[TabId["OUTLINE"] = 1] = "OUTLINE";
    TabId[TabId["ATTACHMENT"] = 2] = "ATTACHMENT"
}
)(TabId || (TabId = {}));
class ViewerPdfSidenavElement extends CrLitElement {
    static get is() {
        return "viewer-pdf-sidenav"
    }
    static get styles() {
        return getCss$f()
    }
    render() {
        return getHtml$c.bind(this)()
    }
    static get properties() {
        return {
            activePage: {
                type: Number
            },
            attachments: {
                type: Array
            },
            bookmarks: {
                type: Array
            },
            clockwiseRotations: {
                type: Number
            },
            docLength: {
                type: Number
            },
            strings: {
                type: Object
            },
            selectedTab_: {
                type: Number
            },
            tabs_: {
                type: Array
            }
        }
    }
    #activePage_accessor_storage = 0;
    get activePage() {
        return this.#activePage_accessor_storage
    }
    set activePage(value) {
        this.#activePage_accessor_storage = value
    }
    #attachments_accessor_storage = [];
    get attachments() {
        return this.#attachments_accessor_storage
    }
    set attachments(value) {
        this.#attachments_accessor_storage = value
    }
    #bookmarks_accessor_storage = [];
    get bookmarks() {
        return this.#bookmarks_accessor_storage
    }
    set bookmarks(value) {
        this.#bookmarks_accessor_storage = value
    }
    #clockwiseRotations_accessor_storage = 0;
    get clockwiseRotations() {
        return this.#clockwiseRotations_accessor_storage
    }
    set clockwiseRotations(value) {
        this.#clockwiseRotations_accessor_storage = value
    }
    #docLength_accessor_storage = 0;
    get docLength() {
        return this.#docLength_accessor_storage
    }
    set docLength(value) {
        this.#docLength_accessor_storage = value
    }
    #strings_accessor_storage;
    get strings() {
        return this.#strings_accessor_storage
    }
    set strings(value) {
        this.#strings_accessor_storage = value
    }
    #selectedTab__accessor_storage = 0;
    get selectedTab_() {
        return this.#selectedTab__accessor_storage
    }
    set selectedTab_(value) {
        this.#selectedTab__accessor_storage = value
    }
    #tabs__accessor_storage = [];
    get tabs_() {
        return this.#tabs__accessor_storage
    }
    set tabs_(value) {
        this.#tabs__accessor_storage = value
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("bookmarks") || changedProperties.has("attachments")) {
            this.tabs_ = this.computeTabs_()
        }
    }
    computeTabs_() {
        const tabs = [{
            id: TabId.THUMBNAIL,
            icon: "pdf:image",
            title: this.strings ? loadTimeData.getString("tooltipThumbnails") : ""
        }];
        if (this.bookmarks.length > 0) {
            tabs.push({
                id: TabId.OUTLINE,
                icon: "pdf:list-alt",
                title: this.strings ? loadTimeData.getString("tooltipDocumentOutline") : ""
            })
        }
        if (this.attachments.length > 0) {
            tabs.push({
                id: TabId.ATTACHMENT,
                icon: "pdf:attach-file",
                title: this.strings ? loadTimeData.getString("tooltipAttachments") : ""
            })
        }
        return tabs
    }
    hideIcons_() {
        return this.tabs_.length === 1
    }
    getTabAriaSelected_(tabId) {
        return this.tabs_[this.selectedTab_].id === tabId ? "true" : "false"
    }
    getTabIndex_(tabId) {
        return this.tabs_[this.selectedTab_].id === tabId ? "0" : "-1"
    }
    getTabSelectedClass_(tabId) {
        return this.tabs_[this.selectedTab_].id === tabId ? "selected" : ""
    }
    onTabClick_(e) {
        const tabId = e.currentTarget.dataset["tabId"];
        assert(tabId !== undefined);
        const tabIdNumber = Number.parseInt(tabId, 10);
        switch (tabIdNumber) {
        case TabId.THUMBNAIL:
            record(UserAction.SELECT_SIDENAV_THUMBNAILS);
            this.selectedTab_ = 0;
            break;
        case TabId.OUTLINE:
            record(UserAction.SELECT_SIDENAV_OUTLINE);
            this.selectedTab_ = 1;
            break;
        case TabId.ATTACHMENT:
            record(UserAction.SELECT_SIDENAV_ATTACHMENT);
            this.selectedTab_ = this.tabs_.length - 1;
            break;
        default:
            assertNotReachedCase()
        }
    }
    hideThumbnailView_() {
        return this.tabs_[this.selectedTab_].id !== TabId.THUMBNAIL
    }
    hideOutlineView_() {
        return this.tabs_[this.selectedTab_].id !== TabId.OUTLINE
    }
    hideAttachmentView_() {
        return this.tabs_[this.selectedTab_].id !== TabId.ATTACHMENT
    }
    onKeydown_(e) {
        if (this.tabs_.length === 1 || e.key !== "ArrowUp" && e.key !== "ArrowDown") {
            return
        }
        e.preventDefault();
        e.stopPropagation();
        if (e.key === "ArrowUp") {
            if (this.selectedTab_ === 0) {
                this.selectedTab_ = this.tabs_.length - 1
            } else {
                this.selectedTab_--
            }
        } else {
            if (this.selectedTab_ === this.tabs_.length - 1) {
                this.selectedTab_ = 0
            } else {
                this.selectedTab_++
            }
        }
    }
}
customElements.define(ViewerPdfSidenavElement.is, ViewerPdfSidenavElement);
let instance$f = null;
function getCss$e() {
    return instance$f || (instance$f = [...[getCss$l()], css`:host{--break-padding:8px}cr-dialog::part(dialog){width:fit-content}table{border-spacing:0}.break>td{--break-color:var(--google-grey-300);border-bottom:1px solid var(--break-color);padding-bottom:var(--break-padding)}.break+tr>td{padding-top:var(--break-padding)}.name{color:var(--cr-primary-text-color);padding-inline-end:12px;vertical-align:top}.value{color:var(--cr-secondary-text-color);max-width:300px;min-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#keywords{white-space:normal}`])
}
function getHtml$b() {
    return html`<!--_html_template_start_-->
<cr-dialog id="dialog" show-on-attach>
  <div slot="title">Document properties</div>
  <div slot="body">
    <table>
      <tr>
        <td class="name">File name:</td>
        <td class="value" id="file-name">${this.fileName}</td>
      </tr>
      <tr class="break">
        <td class="name">File size:</td>
        <td class="value" id="file-size">${this.documentMetadata.fileSize}</td>
      </tr>
      <tr>
        <td class="name">Title:</td>
        <td class="value" id="title">
          ${this.getOrPlaceholder_(this.documentMetadata.title)}
        </td>
      </tr>
      <tr>
        <td class="name">Author:</td>
        <td class="value" id="author">
          ${this.getOrPlaceholder_(this.documentMetadata.author)}
        </td>
      </tr>
      <tr>
        <td class="name">Subject:</td>
        <td class="value" id="subject">
          ${this.getOrPlaceholder_(this.documentMetadata.subject)}
        </td>
      </tr>
      <tr>
        <td class="name">Keywords:</td>
        <td class="value" id="keywords">
          ${this.getOrPlaceholder_(this.documentMetadata.keywords)}
        </td>
      </tr>
      <tr>
        <td class="name">Created:</td>
        <td class="value" id="created">
          ${this.getOrPlaceholder_(this.documentMetadata.creationDate)}
        </td>
      </tr>
      <tr>
        <td class="name">Modified:</td>
        <td class="value" id="modified">
          ${this.getOrPlaceholder_(this.documentMetadata.modDate)}
        </td>
      </tr>
      <tr class="break">
        <td class="name">Application:</td>
        <td class="value" id="application">
          ${this.getOrPlaceholder_(this.documentMetadata.creator)}
        </td>
      </tr>
      <tr>
        <td class="name">PDF producer:</td>
        <td class="value" id="pdf-producer">
          ${this.getOrPlaceholder_(this.documentMetadata.producer)}
        </td>
      </tr>
      <tr>
        <td class="name">PDF version:</td>
        <td class="value" id="pdf-version">
          ${this.getOrPlaceholder_(this.documentMetadata.version)}
        </td>
      </tr>
      <tr>
        <td class="name">Page count:</td>
        <td class="value" id="page-count">${this.pageCount}</td>
      </tr>
      <tr class="break">
        <td class="name">Page size:</td>
        <td class="value" id="page-size">
          ${this.getOrPlaceholder_(this.documentMetadata.pageSize)}
        </td>
      </tr>
      <tr>
        <td class="name">Fast web view:</td>
        <td class="value" id="fast-web-view">
          ${this.getFastWebViewValue_()}
        </td>
      </tr>
    </table>
  </div>
  <div slot="button-container">
    <cr-button id="close" class="action-button" @click="${this.onCloseClick_}">
      Close
    </cr-button>
  </div>
</cr-dialog>
<!--_html_template_end_-->`
}
class ViewerPropertiesDialogElement extends CrLitElement {
    static get is() {
        return "viewer-properties-dialog"
    }
    static get styles() {
        return getCss$e()
    }
    render() {
        return getHtml$b.bind(this)()
    }
    static get properties() {
        return {
            documentMetadata: {
                type: Object
            },
            fileName: {
                type: String
            },
            pageCount: {
                type: Number
            },
            strings: {
                type: Object
            }
        }
    }
    #documentMetadata_accessor_storage = {
        author: "",
        canSerializeDocument: false,
        creationDate: "",
        creator: "",
        fileSize: "",
        keywords: "",
        linearized: false,
        modDate: "",
        pageSize: "",
        producer: "",
        subject: "",
        title: "",
        version: ""
    };
    get documentMetadata() {
        return this.#documentMetadata_accessor_storage
    }
    set documentMetadata(value) {
        this.#documentMetadata_accessor_storage = value
    }
    #fileName_accessor_storage = "";
    get fileName() {
        return this.#fileName_accessor_storage
    }
    set fileName(value) {
        this.#fileName_accessor_storage = value
    }
    #pageCount_accessor_storage = 0;
    get pageCount() {
        return this.#pageCount_accessor_storage
    }
    set pageCount(value) {
        this.#pageCount_accessor_storage = value
    }
    #strings_accessor_storage;
    get strings() {
        return this.#strings_accessor_storage
    }
    set strings(value) {
        this.#strings_accessor_storage = value
    }
    getFastWebViewValue_() {
        if (!this.strings) {
            return ""
        }
        return loadTimeData.getString(this.documentMetadata.linearized ? "propertiesFastWebViewYes" : "propertiesFastWebViewNo")
    }
    getOrPlaceholder_(value) {
        return value || "-"
    }
    onCloseClick_() {
        this.$.dialog.close()
    }
}
customElements.define(ViewerPropertiesDialogElement.is, ViewerPropertiesDialogElement);
let instance$e = null;
function getCss$d() {
    return instance$e || (instance$e = [...[getCss$J()], css`:host{display:block;width:200px;position:relative;overflow:hidden}#progressContainer{position:relative}#progressContainer,:host([indeterminate]) #primaryProgress::after{height:var(--cr-progress-height,4px);background:var(--cr-progress-container-color,var(--google-grey-300))}#primaryProgress,:host([indeterminate]) #primaryProgress::after{position:absolute;top:0;right:0;bottom:0;left:0}#primaryProgress{transform-origin:left center;transform:scaleX(0);will-change:transform;background:var(--cr-progress-active-color,var(--google-green-500))}:host([disabled]) #primaryProgress{background:var(--cr-progress-disabled-active-color,var(--google-grey-500))}:host([indeterminate]:not([disabled])) #primaryProgress{transform-origin:right center;animation:indeterminate-bar var(--cr-progress-indeterminate-cycle-duration,2s) linear infinite}:host([indeterminate]:not([disabled])) #primaryProgress::after{content:'';transform-origin:center center;animation:indeterminate-splitter var(--cr-progress-indeterminate-cycle-duration,2s) linear infinite}@keyframes indeterminate-bar{0%{transform:scaleX(1) translateX(-100%)}50%{transform:scaleX(1) translateX(0%)}75%{transform:scaleX(1) translateX(0%);animation-timing-function:cubic-bezier(.28,.62,.37,.91)}100%{transform:scaleX(0) translateX(0%)}}@keyframes indeterminate-splitter{0%{transform:scaleX(.75) translateX(-125%)}30%{transform:scaleX(.75) translateX(-125%);animation-timing-function:cubic-bezier(.42,0,.6,.8)}90%{transform:scaleX(.75) translateX(125%)}100%{transform:scaleX(.75) translateX(125%)}}`])
}
function getHtml$a() {
    return html`
<div id="progressContainer">
  <div id="primaryProgress"></div>
</div>`
}
class CrProgressElement extends CrLitElement {
    static get is() {
        return "cr-progress"
    }
    static get styles() {
        return getCss$d()
    }
    render() {
        return getHtml$a.bind(this)()
    }
    static get properties() {
        return {
            value: {
                type: Number
            },
            min: {
                type: Number
            },
            max: {
                type: Number
            },
            step: {
                type: Number
            },
            indeterminate: {
                type: Boolean,
                reflect: true
            },
            disabled: {
                type: Boolean,
                reflect: true
            }
        }
    }
    #value_accessor_storage = 0;
    get value() {
        return this.#value_accessor_storage
    }
    set value(value) {
        this.#value_accessor_storage = value
    }
    #min_accessor_storage = 0;
    get min() {
        return this.#min_accessor_storage
    }
    set min(value) {
        this.#min_accessor_storage = value
    }
    #max_accessor_storage = 100;
    get max() {
        return this.#max_accessor_storage
    }
    set max(value) {
        this.#max_accessor_storage = value
    }
    #step_accessor_storage = 1;
    get step() {
        return this.#step_accessor_storage
    }
    set step(value) {
        this.#step_accessor_storage = value
    }
    #indeterminate_accessor_storage = false;
    get indeterminate() {
        return this.#indeterminate_accessor_storage
    }
    set indeterminate(value) {
        this.#indeterminate_accessor_storage = value
    }
    #disabled_accessor_storage = false;
    get disabled() {
        return this.#disabled_accessor_storage
    }
    set disabled(value) {
        this.#disabled_accessor_storage = value
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("min") || changedProperties.has("max") || changedProperties.has("value") || changedProperties.has("step")) {
            const previous = changedProperties.get("value") || 0;
            const clampedValue = this.clampValue_(this.value);
            this.value = Number.isNaN(clampedValue) ? previous : clampedValue
        }
    }
    firstUpdated(changedProperties) {
        super.firstUpdated(changedProperties);
        if (!this.hasAttribute("role")) {
            this.setAttribute("role", "progressbar")
        }
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("min") || changedProperties.has("max") || changedProperties.has("value") || changedProperties.has("step")) {
            const ratio = (this.value - this.min) / (this.max - this.min);
            this.$.primaryProgress.style.transform = `scaleX(${ratio})`;
            this.setAttribute("aria-valuemin", this.min.toString());
            this.setAttribute("aria-valuemax", this.max.toString())
        }
        if (changedProperties.has("indeterminate") || changedProperties.has("value")) {
            if (this.indeterminate) {
                this.removeAttribute("aria-valuenow")
            } else {
                this.setAttribute("aria-valuenow", this.value.toString())
            }
        }
        if (changedProperties.has("disabled")) {
            this.setAttribute("aria-disabled", this.disabled ? "true" : "false")
        }
    }
    clampValue_(value) {
        return Math.min(this.max, Math.max(this.min, this.calcStep_(value)))
    }
    calcStep_(value) {
        value = Number.parseFloat(value.toString());
        if (!this.step) {
            return value
        }
        const numSteps = Math.round((value - this.min) / this.step);
        if (this.step < 1) {
            return numSteps / (1 / this.step) + this.min
        } else {
            return numSteps * this.step + this.min
        }
    }
}
customElements.define(CrProgressElement.is, CrProgressElement);
let instance$d = null;
function getCss$c() {
    return instance$d || (instance$d = [...[getCss$E(), getCss$K()], css`dialog{background:var(--color-theme-color-picker-hue-slider-dialog-background,var(--cr-fallback-color-surface));border:0;border-radius:12px;box-shadow:var(--cr-elevation-3);box-sizing:border-box;color:var(--color-theme-color-picker-hue-slider-dialog-foreground,var(--cr-fallback-color-on-surface));overflow:hidden;margin:0;padding:20px;width:320px;isolation:isolate;position:absolute;z-index:999}a{color:var(--cr-fallback-color-primary)}@media (forced-colors:active){dialog{border:solid 1px Highlight}}#header{display:flex;min-height:24px;gap:8px;padding-bottom:8px}h2{flex:1;font-size:16px;font-weight:500;margin-top:6px;margin-bottom:0}#description{padding-top:4px;padding-bottom:4px;font-size:13px}cr-icon-button{color:var(--cr-fallback-color-on-surface-subtle)}#file-content{flex:1;display:flex;flex-direction:row;gap:8px;padding-top:8px;padding-bottom:8px}#filename-content{display:flex;flex-direction:column;margin-inline-end:auto;line-height:1.5;overflow:hidden;white-space:nowrap;justify-content:center}#pdf-icon{width:20px;height:20px;min-width:20px;min-height:20px;fill:var(--google-red-500);@media (prefers-color-scheme:dark){fill:var(--google-red-300)}}#filename{font-weight:bold;text-overflow:ellipsis;overflow:hidden}#file-metadata{color:var(--cr-fallback-color-on-surface-subtle);font-size:11px;text-overflow:ellipsis;overflow:hidden}cr-progress{width:100%;--cr-progress-active-color:var(--cr-fallback-color-primary);--cr-progress-container-color:var(--cr-fallback-color-neutral-outline)}#footer:has(cr-button){display:flex;flex-direction:row-reverse;padding-top:8px}#footer:empty{padding-top:12px}`])
}
function getHtml$9() {
    return html`<!--_html_template_start_-->
<dialog id="dialog" aria-labelledby="status" @close="${this.onDialogClose_}"
    @focusout="${this.onFocusout_}">
  <div id="header">
    <h2 id="status">${this.dialogTitle_}</h2>
    <cr-icon-button id="close" iron-icon="cr:close"
        aria-label="Close"
        title="Close" @click="${this.onCloseClick_}">
    </cr-icon-button>
  </div>
  <div id="description" .innerHTML="${this.description_}"
      ?hidden="${this.isSaveToDriveState_(SaveToDriveState.UPLOADING)}">
  </div>
  <div id="file-content">
    <cr-icon icon="pdf-save-to-drive:drive-pdf-filled" id="pdf-icon"></cr-icon>
    <div id="filename-content">
      <div id="filename">${this.getFileName_()}</div>
      <div id="file-metadata">${this.getMetadata_()}</div>
    </div>
    ${this.isSaveToDriveState_(SaveToDriveState.UPLOADING) ? html`
      <cr-icon-button id="cancel-upload-button"
          iron-icon="pdf-save-to-drive:cancel"
          aria-label="Cancel upload"
          title="Cancel upload"
          @click="${this.onRequestButtonClick_}">
      </cr-icon-button>
    ` : ""}
  </div>
  <div id="footer">
    ${this.isSaveToDriveState_(SaveToDriveState.UPLOADING) ? html`
      <cr-progress .max="${this.getFileSizeBytes_()}"
          .value="${this.getUploadedBytes_()}">
      </cr-progress>
    ` : ""}
    ${this.isSaveToDriveState_(SaveToDriveState.STORAGE_FULL_ERROR) ? html`
      <cr-button id="manage-storage-button" role="link"
          @click="${this.onRequestButtonClick_}">
        Manage storage
      </cr-button>
    ` : ""}
    ${this.isSaveToDriveState_(SaveToDriveState.SUCCESS) ? html`
      <cr-button id="open-in-drive-button" class="action-button" role="link"
          @click="${this.onRequestButtonClick_}">
        Open in Drive
      </cr-button>
    ` : ""}
    ${this.isSaveToDriveState_(SaveToDriveState.CONNECTION_ERROR) || this.isSaveToDriveState_(SaveToDriveState.SESSION_TIMEOUT_ERROR) ? html`
      <cr-button id="retry-button" class="action-button"
          @click="${this.onRequestButtonClick_}">
        Retry
      </cr-button>
    ` : ""}
  </div>
</dialog>
<!--_html_template_end_-->`
}
const DISMISS_TIMEOUT_MS = 5e3;
const ViewerSaveToDriveBubbleElementBase = I18nMixinLit(CrLitElement);
class ViewerSaveToDriveBubbleElement extends ViewerSaveToDriveBubbleElementBase {
    static get is() {
        return "viewer-save-to-drive-bubble"
    }
    static get styles() {
        return getCss$c()
    }
    render() {
        return getHtml$9.bind(this)()
    }
    static get properties() {
        return {
            docTitle: {
                type: String
            },
            progress: {
                type: Object
            },
            state: {
                type: String
            },
            description_: {
                type: String,
                state: true
            },
            dialogTitle_: {
                type: String,
                state: true
            }
        }
    }
    #docTitle_accessor_storage = "";
    get docTitle() {
        return this.#docTitle_accessor_storage
    }
    set docTitle(value) {
        this.#docTitle_accessor_storage = value
    }
    #progress_accessor_storage = {
        status: chrome.pdfViewerPrivate.SaveToDriveStatus.NOT_STARTED,
        errorType: chrome.pdfViewerPrivate.SaveToDriveErrorType.NO_ERROR
    };
    get progress() {
        return this.#progress_accessor_storage
    }
    set progress(value) {
        this.#progress_accessor_storage = value
    }
    #state_accessor_storage = SaveToDriveState.UNINITIALIZED;
    get state() {
        return this.#state_accessor_storage
    }
    set state(value) {
        this.#state_accessor_storage = value
    }
    #description__accessor_storage = sanitizeInnerHtml("");
    get description_() {
        return this.#description__accessor_storage
    }
    set description_(value) {
        this.#description__accessor_storage = value
    }
    #dialogTitle__accessor_storage = "";
    get dialogTitle_() {
        return this.#dialogTitle__accessor_storage
    }
    set dialogTitle_(value) {
        this.#dialogTitle__accessor_storage = value
    }
    anchor_ = null;
    eventTracker_ = new EventTracker;
    dismissTimeoutId_ = null;
    disconnectedCallback() {
        super.disconnectedCallback();
        this.eventTracker_.removeAll()
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("state")) {
            this.onStateChanged_()
        }
    }
    showAt(anchor, autoDismiss=false) {
        if (this.$.dialog.open && autoDismiss && !this.dismissTimeoutId_) {
            return
        }
        this.$.dialog.show();
        this.anchor_ = anchor;
        this.positionDialog_();
        this.$.dialog.focus();
        this.eventTracker_.remove(window, "resize");
        this.eventTracker_.add(window, "resize", this.positionDialog_.bind(this));
        if (autoDismiss) {
            this.setDismissTimeout_()
        }
    }
    getFileName_() {
        return this.progress.fileName ?? this.docTitle
    }
    getFileSizeBytes_() {
        return this.progress.fileSizeBytes ?? 0
    }
    getMetadata_() {
        return this.progress.fileMetadata ?? ""
    }
    getUploadedBytes_() {
        return this.progress.uploadedBytes ?? 0
    }
    isSaveToDriveState_(state) {
        return this.state === state
    }
    onRequestButtonClick_() {
        let requestType;
        switch (this.state) {
        case SaveToDriveState.UPLOADING:
            requestType = SaveToDriveBubbleRequestType.CANCEL_UPLOAD;
            break;
        case SaveToDriveState.STORAGE_FULL_ERROR:
            requestType = SaveToDriveBubbleRequestType.MANAGE_STORAGE;
            break;
        case SaveToDriveState.SUCCESS:
            requestType = SaveToDriveBubbleRequestType.OPEN_IN_DRIVE;
            break;
        case SaveToDriveState.CONNECTION_ERROR:
        case SaveToDriveState.SESSION_TIMEOUT_ERROR:
            requestType = SaveToDriveBubbleRequestType.RETRY;
            break;
        default:
            assertNotReached(`Invalid bubble action: ${this.state}`)
        }
        this.fire("save-to-drive-bubble-action", requestType);
        this.$.dialog.close()
    }
    onCloseClick_() {
        this.fire("save-to-drive-bubble-action", SaveToDriveBubbleRequestType.DIALOG_CLOSED);
        this.$.dialog.close()
    }
    onDialogClose_() {
        this.eventTracker_.removeAll();
        if (this.dismissTimeoutId_) {
            clearTimeout(this.dismissTimeoutId_);
            this.dismissTimeoutId_ = null
        }
    }
    onFocusout_(e) {
        if (this.$.dialog.contains(e.relatedTarget) || e.composedPath()[0] !== this.$.dialog) {
            return
        }
        this.$.dialog.close()
    }
    onStateChanged_() {
        this.updateDescription_();
        this.updateDialogTitle_()
    }
    positionDialog_() {
        if (!this.anchor_ || !this.$.dialog.open) {
            return
        }
        const anchorBoundingClientRect = this.anchor_.getBoundingClientRect();
        if (isRTL()) {
            this.$.dialog.style.right = `${window.innerWidth - anchorBoundingClientRect.left - this.$.dialog.offsetWidth}px`
        } else {
            this.$.dialog.style.left = `${this.anchor_.offsetLeft + this.anchor_.offsetWidth - this.$.dialog.offsetWidth}px`
        }
        if (anchorBoundingClientRect.bottom + this.$.dialog.offsetHeight >= window.innerHeight) {
            this.$.dialog.style.top = `${this.anchor_.offsetTop - this.$.dialog.offsetHeight}px`
        } else {
            this.$.dialog.style.top = `${this.anchor_.offsetTop + this.anchor_.offsetHeight}px`
        }
    }
    setDismissTimeout_() {
        this.dismissTimeoutId_ = setTimeout(( () => {
            this.dismissTimeoutId_ = null;
            this.$.dialog.close()
        }
        ), DISMISS_TIMEOUT_MS)
    }
    updateDescription_() {
        switch (this.state) {
        case SaveToDriveState.UNINITIALIZED:
        case SaveToDriveState.UPLOADING:
            this.description_ = window.trustedTypes.emptyHTML;
            break;
        case SaveToDriveState.SUCCESS:
            this.description_ = this.i18nAdvanced("saveToDriveDialogSuccessMessage", {
                tags: ["b"],
                substitutions: [this.progress.parentFolderName ?? ""]
            });
            break;
        case SaveToDriveState.CONNECTION_ERROR:
            this.description_ = this.i18nAdvanced("saveToDriveDialogConnectionErrorMessage");
            break;
        case SaveToDriveState.STORAGE_FULL_ERROR:
            this.description_ = this.i18nAdvanced("saveToDriveDialogStorageFullErrorMessage");
            break;
        case SaveToDriveState.SESSION_TIMEOUT_ERROR:
            this.description_ = this.i18nAdvanced("saveToDriveDialogSessionTimeoutErrorMessage");
            break;
        case SaveToDriveState.UNKNOWN_ERROR:
            this.description_ = this.i18nAdvanced("saveToDriveDialogUnknownErrorMessage", {
                tags: ["a"],
                substitutions: [this.i18n("pdfSaveToDriveHelpCenterURL")]
            });
            break;
        default:
            assertNotReached(`Invalid state for description: ${this.state}`)
        }
    }
    updateDialogTitle_() {
        switch (this.state) {
        case SaveToDriveState.UNINITIALIZED:
            this.dialogTitle_ = this.state;
            break;
        case SaveToDriveState.UPLOADING:
            this.dialogTitle_ = this.i18n("saveToDriveDialogUploadingTitle");
            break;
        case SaveToDriveState.SUCCESS:
            this.dialogTitle_ = this.i18n("saveToDriveDialogSuccessTitle");
            break;
        case SaveToDriveState.CONNECTION_ERROR:
        case SaveToDriveState.STORAGE_FULL_ERROR:
        case SaveToDriveState.SESSION_TIMEOUT_ERROR:
        case SaveToDriveState.UNKNOWN_ERROR:
            this.dialogTitle_ = this.i18n("saveToDriveDialogErrorTitle");
            break;
        default:
            assertNotReached(`Invalid state for dialog title: ${this.state}`)
        }
    }
}
customElements.define(ViewerSaveToDriveBubbleElement.is, ViewerSaveToDriveBubbleElement);
let instance$c = null;
function getCss$b() {
    return instance$c || (instance$c = [...[], css`:host{display:contents}#progressRing{width:28px;height:28px;position:absolute;transform:rotate(-90deg)}#innerProgress,#progressTrack{r:90;cx:100;cy:100;fill:transparent;stroke-width:16px}#progressTrack{stroke:rgb(117,117,117);@media (prefers-color-scheme:dark){stroke:var(--cr-fallback-color-neutral-outline)}}#innerProgress{stroke-linecap:round;stroke-dasharray:565.48px;stroke:var(--cr-fallback-color-inverse-primary);@media (prefers-color-scheme:dark){stroke:var(--cr-fallback-color-primary)}}`])
}
function getHtml$8() {
    return html`
<svg id="progressRing" viewBox="-25 -25 250 250" version="1.1"
    xmlns="http://www.w3.org/2000/svg">
  <circle id="progressTrack"></circle>
  <circle id="innerProgress" stroke-dashoffset="${this.strokeDashOffset}">
  </circle>
</svg>`
}
const STROKE_DASHARRAY = 566;
function convertPercentageToStrokeDashOffset(percentage) {
    const ratio = percentage / 100;
    const value = Math.round(STROKE_DASHARRAY * (1 - ratio));
    return `${value}px`
}
class CircularProgressRingElement extends CrLitElement {
    static get is() {
        return "circular-progress-ring"
    }
    static get styles() {
        return getCss$b()
    }
    render() {
        return getHtml$8.bind(this)()
    }
    static get properties() {
        return {
            strokeDashOffset: {
                type: String
            },
            value: {
                type: Number
            }
        }
    }
    #value_accessor_storage = 0;
    get value() {
        return this.#value_accessor_storage
    }
    set value(value) {
        this.#value_accessor_storage = value
    }
    #strokeDashOffset_accessor_storage = `${STROKE_DASHARRAY}px`;
    get strokeDashOffset() {
        return this.#strokeDashOffset_accessor_storage
    }
    set strokeDashOffset(value) {
        this.#strokeDashOffset_accessor_storage = value
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("value")) {
            assert(this.value >= 0 && this.value <= 100);
            this.strokeDashOffset = convertPercentageToStrokeDashOffset(this.value)
        }
    }
}
customElements.define(CircularProgressRingElement.is, CircularProgressRingElement);
let instance$b = null;
function getCss$a() {
    return instance$b || (instance$b = [...[getCss$E(), getCss$n()], css`:host{display:inline-flex;justify-content:center;align-items:center}:host([state='uploading']) #save{z-index:1;--pdf-toolbar-text-color:var(--cr-fallback-color-inverse-primary);@media (prefers-color-scheme:dark){--pdf-toolbar-text-color:var(--cr-fallback-color-primary)}}`])
}
function getHtml$7() {
    return html`<!--_html_template_start_-->
<cr-icon-button id="save" iron-icon="${this.getIronIcon()}"
    @click="${this.onSaveClick}" aria-label="Save to Google Drive"
    aria-haspopup="${this.getAriaHasPopup()}" title="Save to Google Drive">
</cr-icon-button>
${this.isUploading_() ? html`
  <circular-progress-ring .value="${this.progress}"></circular-progress-ring>
` : ""}
<cr-action-menu id="menu">
  <button id="save-edited" class="dropdown-item"
      @click="${this.onSaveEditedClick}">
    With your changes
  </button>
  <button id="save-original" class="dropdown-item"
      @click="${this.onSaveOriginalClick}">
    Without your changes
  </button>
</cr-action-menu>
<!--_html_template_end_-->`
}
const ViewerSaveControlsBase = ViewerSaveControlsMixin(CrLitElement);
class ViewerSaveToDriveControlsElement extends ViewerSaveControlsBase {
    static get is() {
        return "viewer-save-to-drive-controls"
    }
    static get styles() {
        return getCss$a()
    }
    render() {
        return getHtml$7.bind(this)()
    }
    static get properties() {
        return {
            progress: {
                type: Number
            },
            state: {
                type: String,
                reflect: true
            }
        }
    }
    #progress_accessor_storage = 0;
    get progress() {
        return this.#progress_accessor_storage
    }
    set progress(value) {
        this.#progress_accessor_storage = value
    }
    #state_accessor_storage = SaveToDriveState.UNINITIALIZED;
    get state() {
        return this.#state_accessor_storage
    }
    set state(value) {
        this.#state_accessor_storage = value
    }
    getIronIcon() {
        return this.isUploading_() ? "pdf-save-to-drive:arrow-upward-alt" : "pdf-save-to-drive:add-to-drive"
    }
    isUploading_() {
        return this.state === SaveToDriveState.UPLOADING
    }
    getSaveButton() {
        return this.$.save
    }
    getSaveEventType() {
        return "save-to-drive"
    }
    getMenu() {
        return this.$.menu
    }
    shouldShowSaveMenuOnSaveClick(hasEdits) {
        return hasEdits && this.state === SaveToDriveState.UNINITIALIZED
    }
}
customElements.define(ViewerSaveToDriveControlsElement.is, ViewerSaveToDriveControlsElement);
let instance$a = null;
function getCss$9() {
    return instance$a || (instance$a = [...[], css`:host{background-color:var(--viewer-side-background-color);color:var(--google-grey-100);display:block;height:100%;overflow-y:auto;width:288px}.side-panel-content{padding:24px}h2{font-size:13px;font-weight:400;margin:0;margin-inline-start:6px}`])
}
let instance$9 = null;
function getCss$8() {
    return instance$9 || (instance$9 = [...[getCss$E(), getCss$9()], css`:host{--cr-icon-button-margin-end:0;--cr-icon-button-margin-start:0}cr-icon-button{--cr-icon-button-fill-color:var(--viewer-icon-ink-fill-color)}cr-icon-button[data-selected='true']{--cr-icon-button-fill-color:var(--viewer-icon-ink-selected-fill-color);background-color:var(--viewer-icon-ink-selected-background-color)}#brush-options{padding-top:27px}ink-brush-selector{border-bottom:1px solid var(--viewer-border-color);padding:12px 0}ink-color-selector,ink-size-selector{margin:16px 0 32px}`])
}
function getHtml$6() {
    return html`<!--_html_template_start_-->
<ink-brush-selector .currentType="${this.currentType}"
    @current-type-changed="${this.onCurrentTypeChanged}">
</ink-brush-selector>
${this.shouldShowBrushOptions_() ? html`
  <div id="brush-options" class="side-panel-content">
    <h2>Size</h2>
    <ink-size-selector .currentSize="${this.currentSize}"
        .currentType="${this.currentType}"
        @current-size-changed="${this.onCurrentSizeChanged}">
    </ink-size-selector>
    <h2>Color</h2>
    <ink-color-selector label="Color"
        .colors="${this.availableBrushColors()}"
        .currentColor="${this.currentColor}"
        @current-color-changed="${this.onCurrentColorChanged}">
    </ink-color-selector>
  </div>
` : ""}
<!--_html_template_end_-->`
}
const ViewerSidePanelElementBase = InkAnnotationBrushMixin(CrLitElement);
class ViewerSidePanelElement extends ViewerSidePanelElementBase {
    static get is() {
        return "viewer-side-panel"
    }
    static get styles() {
        return getCss$8()
    }
    render() {
        return getHtml$6.bind(this)()
    }
    shouldShowBrushOptions_() {
        return this.currentType !== AnnotationBrushType.ERASER
    }
}
customElements.define(ViewerSidePanelElement.is, ViewerSidePanelElement);
let instance$8 = null;
function getCss$7() {
    return instance$8 || (instance$8 = [...[], css`.md-select{--md-arrow-width:7px;--md-select-bg-color:transparent;--md-select-option-bg-color:white;--md-select-side-padding:10px;--md-select-text-color:inherit;-webkit-appearance:none;background:url(//resources/images/arrow_down.svg) calc(100% - var(--md-select-side-padding)) center no-repeat;background-color:var(--md-select-bg-color);background-size:var(--md-arrow-width);border:solid 1px var(--color-combobox-container-outline,var(--cr-fallback-color-neutral-outline));border-radius:8px;box-sizing:border-box;color:var(--md-select-text-color);cursor:pointer;font-family:inherit;font-size:12px;height:36px;max-width:100%;outline:none;padding-block-end:0;padding-block-start:0;padding-inline-end:calc(var(--md-select-side-padding) + var(--md-arrow-width) + 3px);padding-inline-start:var(--md-select-side-padding);width:var(--md-select-width,200px)}@media (prefers-color-scheme:dark){.md-select{--md-select-option-bg-color:var(--google-grey-900-white-4-percent);background-image:url(//resources/images/dark/arrow_down.svg)}}.md-select:hover{background-color:var(--color-comboxbox-ink-drop-hovered,var(--cr-hover-on-subtle-background-color))}.md-select :-webkit-any(option,optgroup){background-color:var(--md-select-option-bg-color)}.md-select[disabled]{background-color:var(--color-combobox-background-disabled,var(--cr-fallback-color-disabled-background));border-color:transparent;color:var(--color-textfield-foreground-disabled,var(--cr-fallback-color-disabled-foreground));opacity:1;pointer-events:none}.md-select:focus{outline:solid 2px var(--cr-focus-outline-color);outline-offset:-1px}:host-context([dir=rtl]) .md-select{background-position-x:var(--md-select-side-padding)}`])
}
let instance$7 = null;
function getCss$6() {
    return instance$7 || (instance$7 = [...[getCss$r(), getCss$7(), getCss$E()], css`:host{--cr-focus-outline-color:var(--viewer-icon-focus-outline-color);border-radius:16px 16px 0 0;z-index:2}.md-select{--md-select-width:130px;margin-inline-end:8px}.md-select.size-select{--md-select-width:64px;margin-inline-end:var(--toolbar-item-gap)}text-styles-selector{--text-styles-selector-gap:8px}text-alignment-selector{padding:6px}`])
}
function getHtml$5() {
    return html`<!--_html_template_start_-->
<select id="typefaceSelect" class="md-select"
    @change="${this.onTypefaceChange_}" .value="${this.currentTypeface}"
    aria-label="Font">
  ${this.fontNames.map((typeface => html`
    <option value="${typeface}">
      ${this.i18n(this.getLabelForTypeface(typeface))}
    </option>
  `))}
</select>
<select id="sizeSelect" class="md-select size-select"
    @change="${this.onSizeChange_}" .value="${this.currentSize.toString()}"
    aria-label="Font size">
  ${this.sizes.map((size => html`
    <option value="${size}">${size}</option>
  `))}
</select>
<text-styles-selector class="toolbar-icon"></text-styles-selector>
<viewer-bottom-toolbar-dropdown id="alignment" class="toolbar-icon"
    button-title="Text alignment">
  <cr-icon slot="icon" icon="${this.getAlignmentIcon_()}"></cr-icon>
  <text-alignment-selector slot="menu"></text-alignment-selector>
</viewer-bottom-toolbar-dropdown>
<viewer-bottom-toolbar-dropdown id="color" class="toolbar-icon"
    button-title="Text color">
  <div slot="icon" class="color-chip"></div>
  <ink-color-selector slot="menu" label="Text color"
      .colors="${this.colors}" .currentColor="${this.currentColor}"
      @current-color-changed="${this.onCurrentColorChanged}">
  </ink-color-selector>
</viewer-bottom-toolbar-dropdown>
<!--_html_template_end_-->`
}
const ViewerTextBottomToolbarElementBase = InkAnnotationTextMixin(InkTextObserverMixin(I18nMixinLit(CrLitElement)));
class ViewerTextBottomToolbarElement extends ViewerTextBottomToolbarElementBase {
    static get is() {
        return "viewer-text-bottom-toolbar"
    }
    static get styles() {
        return getCss$6()
    }
    render() {
        return getHtml$5.bind(this)()
    }
    static get properties() {
        return {
            currentAlignment_: {
                type: String
            }
        }
    }
    #currentAlignment__accessor_storage = TextAlignment.LEFT;
    get currentAlignment_() {
        return this.#currentAlignment__accessor_storage
    }
    set currentAlignment_(value) {
        this.#currentAlignment__accessor_storage = value
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("currentColor") && this.currentColor) {
            this.style.setProperty("--ink-brush-color", colorToHex(this.currentColor))
        }
    }
    onTypefaceChange_(e) {
        this.onTypefaceSelected(e)
    }
    onSizeChange_(e) {
        this.onSizeSelected(e)
    }
    getAlignmentIcon_() {
        switch (this.currentAlignment_) {
        case TextAlignment.LEFT:
            return "pdf-ink:format-align-left";
        case TextAlignment.CENTER:
            return "pdf-ink:format-align-center";
        case TextAlignment.RIGHT:
            return "pdf-ink:format-align-right";
        default:
            assertNotReached()
        }
    }
    onTextAttributesChanged(attributes) {
        super.onTextAttributesChanged(attributes);
        this.currentAlignment_ = attributes.alignment
    }
}
customElements.define(ViewerTextBottomToolbarElement.is, ViewerTextBottomToolbarElement);
let instance$6 = null;
function getCss$5() {
    return instance$6 || (instance$6 = [...[getCss$7(), getCss$9(), getCss$E()], css`h2{margin-inline-start:0;margin-bottom:8px}.md-select{--md-select-width:240px;margin-top:8px}text-styles-selector{padding-top:8px}text-alignment-selector{padding-top:16px}ink-color-selector{padding-top:4px}.side-panel-content:not(:first-child){padding-top:8px}`])
}
function getHtml$4() {
    return html`<!--_html_template_start_-->
<div class="side-panel-content">
  <h2>Font</h2>
  <select id="typefaceSelect" class="md-select"
      @change="${this.onTypefaceChange_}" .value="${this.currentTypeface}"
      aria-label="Font">
    ${this.fontNames.map((typeface => html`
      <option value="${typeface}">
        ${this.i18n(this.getLabelForTypeface(typeface))}
      </option>
    `))}
  </select>
  <select id="sizeSelect" class="md-select" @change="${this.onSizeChange_}"
      .value="${this.currentSize.toString()}"
      aria-label="Font size">
    ${this.sizes.map((size => html`
      <option value="${size}">${size}</option>
    `))}
  </select>
</div>
<div class="side-panel-content">
  <h2>Styles</h2>
  <text-styles-selector></text-styles-selector>
  <text-alignment-selector></text-alignment-selector>
</div>
<div class="side-panel-content">
  <h2>Text color</h2>
  <ink-color-selector label="Text color" .colors="${this.colors}"
      .currentColor="${this.currentColor}"
      @current-color-changed="${this.onCurrentColorChanged}">
  </ink-color-selector>
</div>
<!--_html_template_end_-->`
}
const ViewerTextSidePanelElementBase = InkAnnotationTextMixin(InkTextObserverMixin(I18nMixinLit(CrLitElement)));
class ViewerTextSidePanelElement extends ViewerTextSidePanelElementBase {
    static get is() {
        return "viewer-text-side-panel"
    }
    static get styles() {
        return getCss$5()
    }
    render() {
        return getHtml$4.bind(this)()
    }
    onTypefaceChange_(e) {
        this.onTypefaceSelected(e)
    }
    onSizeChange_(e) {
        this.onSizeSelected(e)
    }
}
customElements.define(ViewerTextSidePanelElement.is, ViewerTextSidePanelElement);
let instance$5 = null;
function getCss$4() {
    return instance$5 || (instance$5 = [...[getCss$E()], css`:host{--viewer-pdf-toolbar-height:56px;position:relative}:host([more-menu-open_]) #more{background-color:var(--active-button-bg);border-radius:50%}#toolbar{align-items:center;background-color:var(--viewer-pdf-toolbar-background-color);color:white;display:flex;height:var(--viewer-pdf-toolbar-height);padding:0 16px}#title{font-size:0.87rem;font-weight:500;margin-inline-start:16px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#actionMenuTrigger{margin-inline-end:6px}#start{align-items:center;display:flex;overflow:hidden;padding-inline-end:20px}#start,#end{flex:1}#center{align-items:center;display:flex}#end{align-items:center;display:flex;justify-content:flex-end;padding-inline-start:20px;text-align:end;white-space:nowrap}.vertical-separator{background:rgba(255,255,255,0.3);height:20px;width:1px}#zoom-controls{align-items:center;display:flex;padding:0 4px}#zoom-controls input::selection{background-color:var(--viewer-text-input-selection-color)}@media (max-width:600px){#title,#zoom-controls input{display:none}}@media (max-width:500px){#start,#fit{display:none}}@media (max-width:420px){#center{display:none}#end{padding-inline-start:initial;text-align:center}}viewer-page-selector{display:inline-flex;height:36px;margin-inline-end:20px}viewer-page-selector::part(input),input{max-height:var(--viewer-pdf-toolbar-height)}input{background:rgba(0,0,0,0.5);border:none;caret-color:currentColor;color:inherit;font-family:inherit;line-height:inherit;margin:0 4px;outline:none;padding:0 4px;text-align:center;width:5ch}#fit{margin-inline-start:12px}cr-progress{--cr-progress-active-color:var(--google-blue-300);--cr-progress-container-color:transparent;--cr-progress-height:3px;bottom:0;position:absolute;width:100%}cr-progress,#center,#end{transition:opacity 100ms cubic-bezier(0,0,0.2,1)}cr-progress,:host([loading_]) #menuButton,:host([loading_]) #center,:host([loading_]) #end{opacity:0;visibility:hidden}:host([loading_]) cr-progress,#menuButton,#center,#end{opacity:1;visibility:visible}#glic-controls{align-items:center;display:flex}#glic-controls .vertical-separator{margin-inline:6px}#glic-controls cr-icon{margin-bottom:1px}#glic-summarize-button{--cr-button-text-color:#e3e3e3;--cr-focus-outline-color:var(--viewer-icon-focus-outline-color);--cr-hover-background-color:rgba(253,252,251,0.10);border:none;font-weight:400;gap:4px;height:32px;margin-left:2px;padding-inline-end:12px;padding-inline-start:8px}.annotate-button.active{background-color:var(--active-button-bg);border-radius:50%}#annotate-controls{align-items:center;display:flex;margin-inline-start:6px}#annotate-controls .annotate-button.active{--cr-icon-button-fill-color:var(--viewer-icon-ink-selected-fill-color)}#annotate-controls .vertical-separator{margin-inline:6px}viewer-download-controls::part(button),#print,#more{margin-inline-start:4px}.dropdown-item{padding-inline-end:16px;padding-inline-start:12px}.check-container{margin-inline-end:12px;width:16px}cr-action-menu hr{border:none;border-top:var(--cr-separator-line)}`])
}
function getHtml$3() {
    return html`<!--_html_template_start_--><!-- #html_wrapper_imports_start

import {AnnotationMode} from '../constants.js';

#html_wrapper_imports_end -->

<div id="toolbar">
  <div id="start">
    <cr-icon-button id="sidenavToggle" iron-icon="pdf:menu"
        title="Toggle sidebar" aria-label="Toggle sidebar"
        aria-expanded="${this.getAriaExpanded_()}"
        @click="${this.onSidenavToggleClick_}">
    </cr-icon-button>
    <span id="title">${this.docTitle}</span>
  </div>
  <div id="center">
    <viewer-page-selector .docLength="${this.docLength}"
        .pageNo="${this.pageNo}">
    </viewer-page-selector>
    <span class="vertical-separator"></span>
    <span id="zoom-controls">
      <cr-icon-button
          iron-icon="pdf:remove"
          title="Zoom out"
          ?disabled="${this.isAtMinimumZoom_()}"
          aria-label="Zoom out" @click="${this.onZoomOutClick_}">
      </cr-icon-button>
      <input type="text" value="100%"
          aria-label="Zoom level"
          @change="${this.onZoomChange_}"
          @pointerup="${this.onZoomInputPointerup_}"
          @blur="${this.onZoomBlur_}">
      </input>
      <cr-icon-button
          iron-icon="pdf:add"
          title="Zoom in"
          ?disabled="${this.isAtMaximumZoom_()}"
          aria-label="Zoom in" @click="${this.onZoomInClick_}">
      </cr-icon-button>
    </span>
    <span class="vertical-separator"></span>
    <cr-icon-button id="fit" .ironIcon="${this.fitToButtonIcon_()}"
        title="${this.getFitToButtonTooltip_()}"
        aria-label="${this.getFitToButtonTooltip_()}"
        @click="${this.onFitToButtonClick_}">
    </cr-icon-button>
    <cr-icon-button id="rotate" iron-icon="pdf:rotate-90-degrees-ccw"
        suppress-rtl-flip
        aria-label="Rotate counterclockwise" title="Rotate counterclockwise"
        @click="${this.onRotateClick_}">
    </cr-icon-button>

    ${this.showInk2Buttons_() ? html`
      <span id="annotate-controls">
        <span class="vertical-separator"></span>
        ${this.pdfTextAnnotationsEnabled_ ? html`
          <cr-icon-button id="text-annotate" iron-icon="pdf-ink:text-fields"
              class="annotate-button ${this.getActive_(AnnotationMode.TEXT)}"
              @click="${this.onTextAnnotationClick_}"
              ?disabled="${!this.annotationAvailable}"
              aria-pressed="${this.getAriaPressed_(AnnotationMode.TEXT)}"
              aria-label="Add text annotations"
              title="Add text annotations">
          </cr-icon-button>
        ` : ""}
        <cr-icon-button id="annotate" iron-icon="pdf-ink:gesture"
            class="annotate-button ${this.getActive_(AnnotationMode.DRAW)}"
            @click="${this.onAnnotationClick_}"
            ?disabled="${!this.annotationAvailable}"
            aria-pressed="${this.getAriaPressed_(AnnotationMode.DRAW)}"
            aria-label="Draw"
            title="Draw"></cr-icon-button>
        <span class="vertical-separator"></span>
        <cr-icon-button id="undo" ?disabled="${!this.computeEnableUndo_()}"
            iron-icon="pdf:undo"
            @click="${this.onUndoClick_}"
            aria-label="Undo"
            title="Undo"></cr-icon-button>
        <cr-icon-button id="redo" ?disabled="${!this.computeEnableRedo_()}"
            iron-icon="pdf:redo"
            @click="${this.onRedoClick_}"
            aria-label="Redo"
            title="Redo"></cr-icon-button>
      </span>` : ""}

    ${this.pdfGlicSummarizeEnabled_ ? html`
    <span id="glic-controls">
      <span class="vertical-separator"></span>
      <cr-button id="glic-summarize-button"
          aria-label="Summarize"
          title="Summarize with Gemini"
          @click="${this.onGlicSummarizeClick_}">
        <cr-icon slot="prefix-icon" icon="pdf-glic:summarize-auto-2"></cr-icon>
        Summarize
      </cr-button>
    </span>` : ""}
  </div>
  <div id="end">

    ${this.pdfSaveToDriveEnabled ? html`
    <viewer-save-to-drive-controls id="save-to-drive"
        .hasEdits="${this.hasEdits}"

        .hasInk2Edits="${this.hasInk2Edits}"

        .isFormFieldFocused="${this.isFormFieldFocused_()}"
        .progress="${this.saveToDriveProgress}"
        .state="${this.saveToDriveState}">
    </viewer-save-to-drive-controls>` : ""}

    <viewer-download-controls id="downloads"
        .hasEdits="${this.hasEdits}"

        .hasInk2Edits="${this.hasInk2Edits}"

        .isFormFieldFocused="${this.isFormFieldFocused_()}">
    </viewer-download-controls>
    <cr-icon-button id="print" iron-icon="pdf:print"
        ?hidden="${!this.printingEnabled_}" title="Print"
        aria-label="Print" @click="${this.onPrintClick_}">
    </cr-icon-button>
    <cr-icon-button id="more" iron-icon="pdf:more-vert"
        title="More actions" aria-label="More actions"
        @click="${this.onMoreClick_}"></cr-icon-button>
  </div>
</div>
<cr-progress id="progress" .value="${this.loadProgress}"
    ?hidden="${!this.loading_}">
</cr-progress>

<cr-action-menu id="menu" @open-changed="${this.onMoreOpenChanged_}">
  <button id="twoPageViewButton" class="dropdown-item"
      @click="${this.onTwoPageViewClick_}" role="checkbox"
      aria-checked="${this.getAriaChecked_(this.twoUpViewEnabled)}">
    <span class="check-container">
      <cr-icon icon="pdf:check-small"
          ?hidden="${!this.twoUpViewEnabled}"></cr-icon>
    </span>
    Two page view
  </button>

  <button id="show-annotations-button"
      class="dropdown-item" @click="${this.onDisplayAnnotationsClick_}"
      role="checkbox"
      aria-checked="${this.getAriaChecked_(this.displayAnnotations_)}">
    <span class="check-container">
      <cr-icon icon="pdf:check-small"
          ?hidden="${!this.displayAnnotations_}">
      </cr-icon>
    </span>
    Annotations
  </button>

  <hr>

  <button id="presentButton" class="dropdown-item"
      @click="${this.onPresentClick_}"
      ?disabled="${!this.presentationModeAvailable_()}">
    <span class="check-container" aria-hidden="true"></span>
    Present
  </button>

  <button id="properties-button" class="dropdown-item"
      @click="${this.onPropertiesClick_}">
    <span class="check-container" aria-hidden="true"></span>
    Document properties
  </button>
</cr-action-menu>
<!--_html_template_end_-->`
}
class ViewerToolbarElement extends CrLitElement {
    static get is() {
        return "viewer-toolbar"
    }
    static get styles() {
        return getCss$4()
    }
    render() {
        return getHtml$3.bind(this)()
    }
    static get properties() {
        return {
            docTitle: {
                type: String
            },
            docLength: {
                type: Number
            },
            embeddedViewer: {
                type: Boolean
            },
            hasEdits: {
                type: Boolean
            },
            formFieldFocus: {
                type: String
            },
            loadProgress: {
                type: Number
            },
            loading_: {
                type: Boolean,
                reflect: true
            },
            pageNo: {
                type: Number
            },
            rotated: {
                type: Boolean
            },
            strings: {
                type: Object
            },
            viewportZoom: {
                type: Number
            },
            zoomBounds: {
                type: Object
            },
            sidenavCollapsed: {
                type: Boolean
            },
            twoUpViewEnabled: {
                type: Boolean
            },
            moreMenuOpen_: {
                type: Boolean,
                reflect: true
            },
            displayAnnotations_: {
                type: Boolean
            },
            fittingType_: {
                type: String
            },
            printingEnabled_: {
                type: Boolean
            },
            viewportZoomPercent_: {
                type: Number
            },
            pdfGlicSummarizeEnabled_: {
                type: Boolean
            },
            annotationAvailable: {
                type: Boolean
            },
            annotationMode: {
                type: String,
                reflect: true
            },
            enableUndoRedo: {
                type: Boolean
            },
            hasInk2Edits: {
                type: Boolean
            },
            pdfInk2Enabled: {
                type: Boolean
            },
            shouldEnableRedo_: {
                type: Boolean
            },
            shouldEnableUndo_: {
                type: Boolean
            },
            pdfTextAnnotationsEnabled_: {
                type: Boolean
            },
            pdfSaveToDriveEnabled: {
                type: Boolean
            },
            saveToDriveProgress: {
                type: Number
            },
            saveToDriveState: {
                type: String
            }
        }
    }
    #docTitle_accessor_storage = "";
    get docTitle() {
        return this.#docTitle_accessor_storage
    }
    set docTitle(value) {
        this.#docTitle_accessor_storage = value
    }
    #docLength_accessor_storage = 0;
    get docLength() {
        return this.#docLength_accessor_storage
    }
    set docLength(value) {
        this.#docLength_accessor_storage = value
    }
    #embeddedViewer_accessor_storage = false;
    get embeddedViewer() {
        return this.#embeddedViewer_accessor_storage
    }
    set embeddedViewer(value) {
        this.#embeddedViewer_accessor_storage = value
    }
    #hasEdits_accessor_storage = false;
    get hasEdits() {
        return this.#hasEdits_accessor_storage
    }
    set hasEdits(value) {
        this.#hasEdits_accessor_storage = value
    }
    #formFieldFocus_accessor_storage = FormFieldFocusType.NONE;
    get formFieldFocus() {
        return this.#formFieldFocus_accessor_storage
    }
    set formFieldFocus(value) {
        this.#formFieldFocus_accessor_storage = value
    }
    #loadProgress_accessor_storage = 0;
    get loadProgress() {
        return this.#loadProgress_accessor_storage
    }
    set loadProgress(value) {
        this.#loadProgress_accessor_storage = value
    }
    #pageNo_accessor_storage = 0;
    get pageNo() {
        return this.#pageNo_accessor_storage
    }
    set pageNo(value) {
        this.#pageNo_accessor_storage = value
    }
    #rotated_accessor_storage = false;
    get rotated() {
        return this.#rotated_accessor_storage
    }
    set rotated(value) {
        this.#rotated_accessor_storage = value
    }
    #strings_accessor_storage;
    get strings() {
        return this.#strings_accessor_storage
    }
    set strings(value) {
        this.#strings_accessor_storage = value
    }
    #viewportZoom_accessor_storage = 0;
    get viewportZoom() {
        return this.#viewportZoom_accessor_storage
    }
    set viewportZoom(value) {
        this.#viewportZoom_accessor_storage = value
    }
    #zoomBounds_accessor_storage = {
        min: 0,
        max: 0
    };
    get zoomBounds() {
        return this.#zoomBounds_accessor_storage
    }
    set zoomBounds(value) {
        this.#zoomBounds_accessor_storage = value
    }
    #sidenavCollapsed_accessor_storage = false;
    get sidenavCollapsed() {
        return this.#sidenavCollapsed_accessor_storage
    }
    set sidenavCollapsed(value) {
        this.#sidenavCollapsed_accessor_storage = value
    }
    #twoUpViewEnabled_accessor_storage = false;
    get twoUpViewEnabled() {
        return this.#twoUpViewEnabled_accessor_storage
    }
    set twoUpViewEnabled(value) {
        this.#twoUpViewEnabled_accessor_storage = value
    }
    #displayAnnotations__accessor_storage = true;
    get displayAnnotations_() {
        return this.#displayAnnotations__accessor_storage
    }
    set displayAnnotations_(value) {
        this.#displayAnnotations__accessor_storage = value
    }
    #fittingType__accessor_storage = FittingType.FIT_TO_PAGE;
    get fittingType_() {
        return this.#fittingType__accessor_storage
    }
    set fittingType_(value) {
        this.#fittingType__accessor_storage = value
    }
    #moreMenuOpen__accessor_storage = false;
    get moreMenuOpen_() {
        return this.#moreMenuOpen__accessor_storage
    }
    set moreMenuOpen_(value) {
        this.#moreMenuOpen__accessor_storage = value
    }
    #loading__accessor_storage = true;
    get loading_() {
        return this.#loading__accessor_storage
    }
    set loading_(value) {
        this.#loading__accessor_storage = value
    }
    #printingEnabled__accessor_storage = false;
    get printingEnabled_() {
        return this.#printingEnabled__accessor_storage
    }
    set printingEnabled_(value) {
        this.#printingEnabled__accessor_storage = value
    }
    #viewportZoomPercent__accessor_storage = 0;
    get viewportZoomPercent_() {
        return this.#viewportZoomPercent__accessor_storage
    }
    set viewportZoomPercent_(value) {
        this.#viewportZoomPercent__accessor_storage = value
    }
    #pdfGlicSummarizeEnabled__accessor_storage = false;
    get pdfGlicSummarizeEnabled_() {
        return this.#pdfGlicSummarizeEnabled__accessor_storage
    }
    set pdfGlicSummarizeEnabled_(value) {
        this.#pdfGlicSummarizeEnabled__accessor_storage = value
    }
    #pdfSaveToDriveEnabled_accessor_storage = false;
    get pdfSaveToDriveEnabled() {
        return this.#pdfSaveToDriveEnabled_accessor_storage
    }
    set pdfSaveToDriveEnabled(value) {
        this.#pdfSaveToDriveEnabled_accessor_storage = value
    }
    #saveToDriveProgress_accessor_storage = 0;
    get saveToDriveProgress() {
        return this.#saveToDriveProgress_accessor_storage
    }
    set saveToDriveProgress(value) {
        this.#saveToDriveProgress_accessor_storage = value
    }
    #saveToDriveState_accessor_storage = SaveToDriveState.UNINITIALIZED;
    get saveToDriveState() {
        return this.#saveToDriveState_accessor_storage
    }
    set saveToDriveState(value) {
        this.#saveToDriveState_accessor_storage = value
    }
    #annotationAvailable_accessor_storage = false;
    get annotationAvailable() {
        return this.#annotationAvailable_accessor_storage
    }
    set annotationAvailable(value) {
        this.#annotationAvailable_accessor_storage = value
    }
    #annotationMode_accessor_storage = AnnotationMode.OFF;
    get annotationMode() {
        return this.#annotationMode_accessor_storage
    }
    set annotationMode(value) {
        this.#annotationMode_accessor_storage = value
    }
    #enableUndoRedo_accessor_storage = true;
    get enableUndoRedo() {
        return this.#enableUndoRedo_accessor_storage
    }
    set enableUndoRedo(value) {
        this.#enableUndoRedo_accessor_storage = value
    }
    #hasInk2Edits_accessor_storage = false;
    get hasInk2Edits() {
        return this.#hasInk2Edits_accessor_storage
    }
    set hasInk2Edits(value) {
        this.#hasInk2Edits_accessor_storage = value
    }
    #pdfInk2Enabled_accessor_storage = false;
    get pdfInk2Enabled() {
        return this.#pdfInk2Enabled_accessor_storage
    }
    set pdfInk2Enabled(value) {
        this.#pdfInk2Enabled_accessor_storage = value
    }
    #shouldEnableRedo__accessor_storage = false;
    get shouldEnableRedo_() {
        return this.#shouldEnableRedo__accessor_storage
    }
    set shouldEnableRedo_(value) {
        this.#shouldEnableRedo__accessor_storage = value
    }
    #shouldEnableUndo__accessor_storage = false;
    get shouldEnableUndo_() {
        return this.#shouldEnableUndo__accessor_storage
    }
    set shouldEnableUndo_(value) {
        this.#shouldEnableUndo__accessor_storage = value
    }
    #pdfTextAnnotationsEnabled__accessor_storage = false;
    get pdfTextAnnotationsEnabled_() {
        return this.#pdfTextAnnotationsEnabled__accessor_storage
    }
    set pdfTextAnnotationsEnabled_(value) {
        this.#pdfTextAnnotationsEnabled__accessor_storage = value
    }
    canUndo_ = false;
    canRedo_ = false;
    pluginController_ = PluginController.getInstance();
    strokeInProgress_ = false;
    tracker_ = new EventTracker;
    constructor() {
        super();
        this.tracker_.add(this.pluginController_.getEventTarget(), PluginControllerEventType.FINISH_INK_STROKE, this.handleFinishInkStroke_.bind(this));
        this.tracker_.add(this.pluginController_.getEventTarget(), PluginControllerEventType.START_INK_STROKE, this.handleStartInkStroke_.bind(this));
        this.tracker_.add(Ink2Manager.getInstance(), "undo-redo-state-changed", this.handleUndoRedoStateChanged_.bind(this))
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("loadProgress")) {
            this.loading_ = this.loadProgress < 100
        }
        if (changedProperties.has("strings") && this.strings) {
            this.updateLoadTimeData_()
        }
        if (changedProperties.has("viewportZoom")) {
            this.viewportZoomPercent_ = Math.round(100 * this.viewportZoom)
        }
        if (changedProperties.has("formFieldFocus")) {
            this.updateCanUndoRedo_()
        }
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("viewportZoom")) {
            this.getZoomInput_().value = `${this.viewportZoomPercent_}%`
        }
    }
    updateLoadTimeData_() {
        this.printingEnabled_ = loadTimeData.getBoolean("printingEnabled");
        this.pdfGlicSummarizeEnabled_ = loadTimeData.getBoolean("pdfGlicSummarizeEnabled");
        this.pdfTextAnnotationsEnabled_ = loadTimeData.getBoolean("pdfTextAnnotationsEnabled")
    }
    onSidenavToggleClick_() {
        record(UserAction.TOGGLE_SIDENAV);
        this.dispatchEvent(new CustomEvent("sidenav-toggle-click"))
    }
    fitToButtonIcon_() {
        return "pdf" + (this.fittingType_ === FittingType.FIT_TO_PAGE ? ":fit-page-height" : ":fit-page-width")
    }
    getFitToButtonTooltip_() {
        if (!this.strings) {
            return ""
        }
        return loadTimeData.getString(this.fittingType_ === FittingType.FIT_TO_PAGE ? "tooltipFitToPage" : "tooltipFitToWidth")
    }
    onGlicSummarizeClick_() {
        this.fire("glic-summarize")
    }
    showInk2Buttons_() {
        return this.pdfInk2Enabled
    }
    onPrintClick_() {
        this.dispatchEvent(new CustomEvent("print"))
    }
    onRotateClick_() {
        this.dispatchEvent(new CustomEvent("rotate-left"))
    }
    onDisplayAnnotationsClick_() {
        record(UserAction.TOGGLE_DISPLAY_ANNOTATIONS);
        this.displayAnnotations_ = !this.displayAnnotations_;
        this.dispatchEvent(new CustomEvent("display-annotations-changed",{
            detail: this.displayAnnotations_
        }));
        this.$.menu.close()
    }
    onPresentClick_() {
        record(UserAction.PRESENT);
        this.$.menu.close();
        this.dispatchEvent(new CustomEvent("present-click"))
    }
    onPropertiesClick_() {
        record(UserAction.PROPERTIES);
        this.$.menu.close();
        this.dispatchEvent(new CustomEvent("properties-click"))
    }
    getAriaChecked_(checked) {
        return checked ? "true" : "false"
    }
    getAriaExpanded_() {
        return this.sidenavCollapsed ? "false" : "true"
    }
    onTwoPageViewClick_() {
        const newTwoUpViewEnabled = !this.twoUpViewEnabled;
        this.dispatchEvent(new CustomEvent("two-up-view-changed",{
            detail: newTwoUpViewEnabled
        }));
        this.$.menu.close()
    }
    onZoomInClick_() {
        this.dispatchEvent(new CustomEvent("zoom-in"))
    }
    onZoomOutClick_() {
        this.dispatchEvent(new CustomEvent("zoom-out"))
    }
    forceFit(fittingType) {
        this.fittingType_ = fittingType === FittingType.FIT_TO_WIDTH ? FittingType.FIT_TO_PAGE : FittingType.FIT_TO_WIDTH
    }
    fitToggle() {
        const newState = this.fittingType_ === FittingType.FIT_TO_PAGE ? FittingType.FIT_TO_WIDTH : FittingType.FIT_TO_PAGE;
        this.dispatchEvent(new CustomEvent("fit-to-changed",{
            detail: this.fittingType_
        }));
        this.fittingType_ = newState
    }
    onFitToButtonClick_() {
        this.fitToggle()
    }
    getZoomInput_() {
        return this.shadowRoot.querySelector("#zoom-controls input")
    }
    onZoomBlur_() {
        this.onZoomChange_()
    }
    onZoomChange_() {
        const input = this.getZoomInput_();
        let value = Number.parseInt(input.value, 10);
        value = Math.max(Math.min(value, this.zoomBounds.max), this.zoomBounds.min);
        if (this.sendZoomChanged_(value)) {
            return
        }
        const zoomString = `${this.viewportZoomPercent_}%`;
        input.value = zoomString
    }
    sendZoomChanged_(value) {
        if (Number.isNaN(value)) {
            return false
        }
        if (Math.abs(this.viewportZoom * 100 - value) < .5) {
            return false
        }
        this.dispatchEvent(new CustomEvent("zoom-changed",{
            detail: value
        }));
        return true
    }
    onZoomInputPointerup_(e) {
        e.target.select()
    }
    onMoreClick_() {
        const anchor = this.shadowRoot.querySelector("#more");
        this.$.menu.showAt(anchor, {
            anchorAlignmentX: AnchorAlignment.CENTER,
            anchorAlignmentY: AnchorAlignment.AFTER_END,
            noOffset: true
        })
    }
    onMoreOpenChanged_(e) {
        this.moreMenuOpen_ = e.detail.value
    }
    isAtMinimumZoom_() {
        return this.zoomBounds !== undefined && this.viewportZoomPercent_ === this.zoomBounds.min
    }
    isAtMaximumZoom_() {
        return this.zoomBounds !== undefined && this.viewportZoomPercent_ === this.zoomBounds.max
    }
    getActive_(mode) {
        return mode === this.annotationMode ? "active" : ""
    }
    getAriaPressed_(mode) {
        return mode === this.annotationMode ? "true" : "false"
    }
    onAnnotationClick_() {
        assert(this.pdfInk2Enabled);
        const newAnnotationMode = this.annotationMode === AnnotationMode.DRAW ? AnnotationMode.OFF : AnnotationMode.DRAW;
        this.setAnnotationMode(newAnnotationMode)
    }
    setAnnotationMode(annotationMode) {
        assert(this.pdfInk2Enabled);
        this.dispatchEvent(new CustomEvent("annotation-mode-updated",{
            detail: annotationMode
        }))
    }
    onTextAnnotationClick_() {
        this.setAnnotationMode(this.annotationMode === AnnotationMode.TEXT ? AnnotationMode.OFF : AnnotationMode.TEXT)
    }
    handleStartInkStroke_() {
        this.strokeInProgress_ = true
    }
    handleFinishInkStroke_() {
        this.strokeInProgress_ = false
    }
    computeEnableUndo_() {
        return this.shouldEnableUndo_ && !this.strokeInProgress_ && this.enableUndoRedo
    }
    computeEnableRedo_() {
        return this.shouldEnableRedo_ && !this.strokeInProgress_ && this.enableUndoRedo
    }
    onUndoClick_() {
        this.undo()
    }
    undo() {
        if (!this.computeEnableUndo_()) {
            return
        }
        assert(this.formFieldFocus !== FormFieldFocusType.TEXT);
        Ink2Manager.getInstance().undo();
        getInstance().announce(loadTimeData.getString("ink2AnnotationUndone"));
        record(UserAction.UNDO_INK2)
    }
    onRedoClick_() {
        this.redo()
    }
    redo() {
        if (!this.computeEnableRedo_()) {
            return
        }
        assert(this.formFieldFocus !== FormFieldFocusType.TEXT);
        Ink2Manager.getInstance().redo();
        getInstance().announce(loadTimeData.getString("ink2AnnotationRedone"));
        record(UserAction.REDO_INK2)
    }
    updateCanUndoRedo_() {
        const isTextFormFieldFocused = this.formFieldFocus === FormFieldFocusType.TEXT;
        this.shouldEnableUndo_ = !isTextFormFieldFocused && this.canUndo_;
        this.shouldEnableRedo_ = !isTextFormFieldFocused && this.canRedo_
    }
    handleUndoRedoStateChanged_(e) {
        this.canUndo_ = e.detail.canUndo;
        this.canRedo_ = e.detail.canRedo;
        this.updateCanUndoRedo_()
    }
    isFormFieldFocused_() {
        return this.formFieldFocus !== FormFieldFocusType.NONE
    }
    presentationModeAvailable_() {
        return !this.embeddedViewer
    }
    getSaveToDriveBubbleAnchor() {
        const anchor = this.shadowRoot.querySelector("#save-to-drive");
        assert(anchor);
        return anchor
    }
}
customElements.define(ViewerToolbarElement.is, ViewerToolbarElement);
class NavigatorDelegateImpl {
    browserApi_;
    constructor(browserApi) {
        this.browserApi_ = browserApi
    }
    navigateInCurrentTab(url) {
        this.browserApi_.navigateInCurrentTab(url)
    }
    navigateInNewTab(url, active) {
        if (chrome.tabs) {
            chrome.tabs.create({
                url: url,
                active: active
            })
        } else {
            window.open(url)
        }
    }
    navigateInNewWindow(url) {
        if (chrome.windows) {
            chrome.windows.create({
                url: url
            })
        } else {
            window.open(url, "_blank")
        }
    }
    isAllowedLocalFileAccess(url) {
        return new Promise((resolve => {
            chrome.pdfViewerPrivate.isAllowedLocalFileAccess(url, (result => resolve(result)))
        }
        ))
    }
}
class PdfNavigatorImpl {
    originalUrl_ = null;
    viewport_;
    paramsParser_;
    navigatorDelegate_;
    constructor(originalUrl, viewport, paramsParser, navigatorDelegate) {
        try {
            this.originalUrl_ = new URL(originalUrl)
        } catch (err) {
            console.warn("Invalid original URL")
        }
        this.viewport_ = viewport;
        this.paramsParser_ = paramsParser;
        this.navigatorDelegate_ = navigatorDelegate
    }
    async navigate(urlString, disposition) {
        if (urlString.length === 0) {
            return Promise.resolve()
        }
        if (urlString[0] === "#" && this.originalUrl_) {
            const newUrl = new URL(this.originalUrl_.href);
            newUrl.hash = urlString;
            urlString = newUrl.href
        }
        if (!urlString.includes("://") && !urlString.includes("mailto:")) {
            urlString = await this.guessUrlWithoutScheme_(urlString)
        }
        let url = null;
        try {
            url = new URL(urlString)
        } catch (err) {
            return Promise.reject(err)
        }
        if (!await this.isValidUrl_(url)) {
            return Promise.resolve()
        }
        let whenDone = Promise.resolve();
        switch (disposition) {
        case WindowOpenDisposition.CURRENT_TAB:
            whenDone = this.paramsParser_.getViewportFromUrlParams(url.href).then(this.onViewportReceived_.bind(this));
            break;
        case WindowOpenDisposition.NEW_BACKGROUND_TAB:
            this.navigatorDelegate_.navigateInNewTab(url.href, false);
            break;
        case WindowOpenDisposition.NEW_FOREGROUND_TAB:
            this.navigatorDelegate_.navigateInNewTab(url.href, true);
            break;
        case WindowOpenDisposition.NEW_WINDOW:
            this.navigatorDelegate_.navigateInNewWindow(url.href);
            break;
        case WindowOpenDisposition.SAVE_TO_DISK:
            whenDone = this.paramsParser_.getViewportFromUrlParams(url.href).then(this.onViewportReceived_.bind(this));
            break
        }
        return whenDone
    }
    onViewportReceived_(viewportPosition) {
        let newUrl = null;
        try {
            newUrl = new URL(viewportPosition.url)
        } catch (err) {}
        const pageNumber = viewportPosition.page;
        if (pageNumber !== undefined && this.originalUrl_ && newUrl && this.originalUrl_.origin === newUrl.origin && this.originalUrl_.pathname === newUrl.pathname) {
            this.viewport_.goToPage(pageNumber)
        } else {
            this.navigatorDelegate_.navigateInCurrentTab(viewportPosition.url)
        }
    }
    async isValidUrl_(url) {
        const validSchemes = ["http:", "https:", "ftp:", "file:", "mailto:"];
        if (!validSchemes.includes(url.protocol)) {
            return false
        }
        if (url.protocol === "file:" && this.originalUrl_ && this.originalUrl_.protocol !== "file:") {
            return this.navigatorDelegate_.isAllowedLocalFileAccess(this.originalUrl_.toString())
        }
        return true
    }
    async guessUrlWithoutScheme_(url) {
        if (!this.originalUrl_ || this.originalUrl_.protocol === "mailto:" || !await this.isValidUrl_(this.originalUrl_)) {
            return url
        }
        if (url.startsWith("/")) {
            return this.originalUrl_.origin + url
        }
        if (url.startsWith("\\")) {
            url = "./" + url
        }
        if (!url.startsWith(".")) {
            const domainSeparatorIndex = url.indexOf("/");
            const domainName = domainSeparatorIndex === -1 ? url : url.substr(0, domainSeparatorIndex);
            const domainDotCount = (domainName.match(/\./g) || []).length;
            if (domainDotCount >= 2) {
                return "http://" + url
            }
        }
        return new URL(url,this.originalUrl_.href).href
    }
}
var WindowOpenDisposition;
(function(WindowOpenDisposition) {
    WindowOpenDisposition[WindowOpenDisposition["CURRENT_TAB"] = 1] = "CURRENT_TAB";
    WindowOpenDisposition[WindowOpenDisposition["NEW_FOREGROUND_TAB"] = 3] = "NEW_FOREGROUND_TAB";
    WindowOpenDisposition[WindowOpenDisposition["NEW_BACKGROUND_TAB"] = 4] = "NEW_BACKGROUND_TAB";
    WindowOpenDisposition[WindowOpenDisposition["NEW_WINDOW"] = 6] = "NEW_WINDOW";
    WindowOpenDisposition[WindowOpenDisposition["SAVE_TO_DISK"] = 7] = "SAVE_TO_DISK"
}
)(WindowOpenDisposition || (WindowOpenDisposition = {}));
Object.assign(window, {
    PdfNavigatorImpl: PdfNavigatorImpl,
    WindowOpenDisposition: WindowOpenDisposition
});
const CrSelectableMixin = superClass => {
    class CrSelectableMixin extends superClass {
        static get properties() {
            return {
                attrForSelected: {
                    type: String
                },
                selected: {
                    type: String,
                    notify: true
                },
                selectedAttribute: {
                    type: String
                },
                selectable: {
                    type: String
                }
            }
        }
        #attrForSelected_accessor_storage = null;
        get attrForSelected() {
            return this.#attrForSelected_accessor_storage
        }
        set attrForSelected(value) {
            this.#attrForSelected_accessor_storage = value
        }
        #selectable_accessor_storage;
        get selectable() {
            return this.#selectable_accessor_storage
        }
        set selectable(value) {
            this.#selectable_accessor_storage = value
        }
        #selected_accessor_storage;
        get selected() {
            return this.#selected_accessor_storage
        }
        set selected(value) {
            this.#selected_accessor_storage = value
        }
        #selectedAttribute_accessor_storage = null;
        get selectedAttribute() {
            return this.#selectedAttribute_accessor_storage
        }
        set selectedAttribute(value) {
            this.#selectedAttribute_accessor_storage = value
        }
        selectOnClick = true;
        items_ = [];
        selectedItem_ = null;
        firstUpdated(changedProperties) {
            super.firstUpdated(changedProperties);
            if (this.selectOnClick) {
                this.addEventListener("click", (e => this.onClick_(e)))
            }
            this.observeItems()
        }
        observeItems() {
            this.getSlot().addEventListener("slotchange", ( () => this.itemsChanged()))
        }
        connectedCallback() {
            super.connectedCallback();
            this.updateItems_()
        }
        willUpdate(changedProperties) {
            super.willUpdate(changedProperties);
            if (changedProperties.has("attrForSelected")) {
                if (this.selectedItem_) {
                    assert(this.attrForSelected);
                    const value = this.selectedItem_.getAttribute(this.attrForSelected);
                    assert(value !== null);
                    this.selected = value
                }
            }
        }
        updated(changedProperties) {
            super.updated(changedProperties);
            if (changedProperties.has("selected")) {
                this.updateSelectedItem_()
            }
        }
        select(value) {
            this.selected = value
        }
        selectPrevious() {
            const length = this.items_.length;
            let index = length - 1;
            if (this.selected !== undefined) {
                index = (this.valueToIndex_(this.selected) - 1 + length) % length
            }
            this.selected = this.indexToValue_(index)
        }
        selectNext() {
            const index = this.selected === undefined ? 0 : (this.valueToIndex_(this.selected) + 1) % this.items_.length;
            this.selected = this.indexToValue_(index)
        }
        getItemsForTest() {
            return this.items_
        }
        getSlot() {
            const slot = this.shadowRoot.querySelector("slot");
            assert(slot);
            return slot
        }
        queryItems() {
            const selectable = this.selectable === undefined ? "*" : this.selectable;
            return Array.from(this.querySelectorAll(`:scope > ${selectable}`))
        }
        queryMatchingItem(selector) {
            const selectable = this.selectable || "*";
            return this.querySelector(`:scope > :is(${selectable})${selector}`)
        }
        updateItems_() {
            this.items_ = this.queryItems();
            this.items_.forEach(( (item, index) => item.setAttribute("data-selection-index", index.toString())))
        }
        get selectedItem() {
            return this.selectedItem_
        }
        updateSelectedItem_() {
            if (!this.items_) {
                return
            }
            const item = this.selected == null ? null : this.items_[this.valueToIndex_(this.selected)];
            if (!!item && this.selectedItem_ !== item) {
                this.setItemSelected_(this.selectedItem_, false);
                this.setItemSelected_(item, true)
            } else if (!item) {
                this.setItemSelected_(this.selectedItem_, false)
            }
        }
        setItemSelected_(item, isSelected) {
            if (!item) {
                return
            }
            item.classList.toggle("selected", isSelected);
            if (this.selectedAttribute) {
                item.toggleAttribute(this.selectedAttribute, isSelected)
            }
            this.selectedItem_ = isSelected ? item : null;
            this.fire("iron-" + (isSelected ? "select" : "deselect"), {
                item: item
            })
        }
        valueToIndex_(value) {
            if (!this.attrForSelected) {
                return Number(value)
            }
            const match = this.queryMatchingItem(`[${this.attrForSelected}="${value}"]`);
            return match ? Number(match.dataset["selectionIndex"]) : -1
        }
        indexToValue_(index) {
            if (!this.attrForSelected) {
                return index
            }
            const item = this.items_[index];
            if (!item) {
                return index
            }
            return item.getAttribute(this.attrForSelected) || index
        }
        itemsChanged() {
            this.updateItems_();
            this.updateSelectedItem_();
            this.fire("iron-items-changed")
        }
        onClick_(e) {
            let element = e.target;
            while (element && element !== this) {
                const idx = this.items_.indexOf(element);
                if (idx >= 0) {
                    const value = this.indexToValue_(idx);
                    assert(value !== null);
                    this.fire("iron-activate", {
                        item: element,
                        selected: value
                    });
                    this.select(value);
                    return
                }
                element = element.parentNode
            }
        }
    }
    return CrSelectableMixin
}
;
let instance$4 = null;
function getCss$3() {
    return instance$4 || (instance$4 = [...[], css`:host{display:block}:host(:not([show-all]))>::slotted(:not(slot):not(.selected)){display:none !important}`])
}
function getHtml$2() {
    return html`<slot></slot>`
}
const CrPageSelectorElementBase = CrSelectableMixin(CrLitElement);
class CrPageSelectorElement extends CrPageSelectorElementBase {
    static get is() {
        return "cr-page-selector"
    }
    static get styles() {
        return getCss$3()
    }
    render() {
        return getHtml$2.bind(this)()
    }
    static get properties() {
        return {
            hasNestedSlots: {
                type: Boolean
            }
        }
    }
    #hasNestedSlots_accessor_storage = false;
    get hasNestedSlots() {
        return this.#hasNestedSlots_accessor_storage
    }
    set hasNestedSlots(value) {
        this.#hasNestedSlots_accessor_storage = value
    }
    constructor() {
        super();
        this.selectOnClick = false
    }
    queryItems() {
        return this.hasNestedSlots ? Array.from(this.getSlot().assignedElements({
            flatten: true
        })) : super.queryItems()
    }
    queryMatchingItem(selector) {
        if (this.hasNestedSlots) {
            const match = this.queryItems().find((el => el.matches(selector)));
            return match ? match : null
        }
        return super.queryMatchingItem(selector)
    }
    observeItems() {
        if (this.hasNestedSlots) {
            this.addEventListener("slotchange", ( () => this.itemsChanged()))
        }
        super.observeItems()
    }
}
customElements.define(CrPageSelectorElement.is, CrPageSelectorElement);
let instance$3 = null;
function getCss$2() {
    return instance$3 || (instance$3 = [...[], css`:host{--cr-toast-background:var(--color-toast-background,var(--cr-fallback-color-inverse-surface));--cr-toast-button-color:var(--color-toast-button,var(--cr-fallback-color-inverse-primary));--cr-toast-text-color:var(--color-toast-foreground,var(--cr-fallback-color-inverse-on-surface));--cr-focus-outline-color:var(--cr-focus-outline-inverse-color);align-items:center;background:var(--cr-toast-background);border-radius:8px;bottom:0;box-shadow:0 2px 4px 0 rgba(0,0,0,0.28);box-sizing:border-box;display:flex;line-height:20px;margin:24px;max-width:var(--cr-toast-max-width,568px);min-height:52px;min-width:288px;opacity:0;padding:0 16px;position:fixed;transform:translateY(100px);transition:opacity 300ms,transform 300ms;visibility:hidden;z-index:1}:host-context([dir=ltr]){left:0}:host-context([dir=rtl]){right:0}:host([open]){opacity:1;transform:translateY(0);visibility:visible}:host(:not([open])) ::slotted(*){display:none}:host ::slotted(*){color:var(--cr-toast-text-color)}:host ::slotted(cr-button){background-color:transparent !important;border:none !important;color:var(--cr-toast-button-color) !important;margin-inline-start:32px !important;min-width:52px !important;padding:8px !important}:host ::slotted(cr-button:hover){background-color:transparent !important}::slotted(cr-button:last-of-type){margin-inline-end:-8px}`])
}
function getHtml$1() {
    return html`<slot></slot>`
}
class CrToastElement extends CrLitElement {
    static get is() {
        return "cr-toast"
    }
    static get styles() {
        return getCss$2()
    }
    render() {
        return getHtml$1.bind(this)()
    }
    static get properties() {
        return {
            duration: {
                type: Number
            },
            open: {
                type: Boolean,
                reflect: true
            }
        }
    }
    #duration_accessor_storage = 0;
    get duration() {
        return this.#duration_accessor_storage
    }
    set duration(value) {
        this.#duration_accessor_storage = value
    }
    #open_accessor_storage = false;
    get open() {
        return this.#open_accessor_storage
    }
    set open(value) {
        this.#open_accessor_storage = value
    }
    hideTimeoutId_ = null;
    constructor() {
        super();
        this.addEventListener("focusin", this.clearTimeout_);
        this.addEventListener("focusout", this.resetAutoHide_)
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        if (changedProperties.has("duration") || changedProperties.has("open")) {
            this.resetAutoHide_()
        }
    }
    clearTimeout_() {
        if (this.hideTimeoutId_ !== null) {
            window.clearTimeout(this.hideTimeoutId_);
            this.hideTimeoutId_ = null
        }
    }
    resetAutoHide_() {
        this.clearTimeout_();
        if (this.open && this.duration !== 0) {
            this.hideTimeoutId_ = window.setTimeout(( () => {
                this.hide()
            }
            ), this.duration)
        }
    }
    async show() {
        const shouldResetAutohide = this.open;
        this.removeAttribute("role");
        this.open = true;
        await this.updateComplete;
        this.setAttribute("role", "alert");
        if (shouldResetAutohide) {
            this.resetAutoHide_()
        }
    }
    async hide() {
        this.open = false;
        await this.updateComplete
    }
}
customElements.define(CrToastElement.is, CrToastElement);
class LocalStorageProxyImpl {
    getItem(key) {
        return window.localStorage ? window.localStorage.getItem(key) : null
    }
    setItem(key, value) {
        if (window.localStorage) {
            window.localStorage.setItem(key, value)
        }
    }
    static getInstance() {
        return instance$2 || (instance$2 = new LocalStorageProxyImpl)
    }
}
let instance$2 = null;
let instance$1 = null;
function getCss$1() {
    return instance$1 || (instance$1 = [...[], css`.spinner{--cr-spinner-size:28px;mask-image:url(//resources/images/throbber_small.svg);mask-position:center;mask-repeat:no-repeat;mask-size:var(--cr-spinner-size) var(--cr-spinner-size);background-color:var(--cr-spinner-color,var(--google-blue-500));height:var(--cr-spinner-size);width:var(--cr-spinner-size)}@media (prefers-color-scheme:dark){.spinner{background-color:var(--cr-spinner-color,var(--google-blue-300))}}`])
}
let instance = null;
function getCss() {
    return instance || (instance = [...[getCss$L(), getCss$J(), getCss$1()], css`:host{--viewer-pdf-sidenav-width:300px;display:flex;flex-direction:column;height:100%;width:100%}viewer-pdf-sidenav,viewer-toolbar{--pdf-toolbar-text-color:rgb(241,241,241)}#side-panel{border-inline-start:1px solid var(--viewer-border-color)}viewer-toolbar{--active-button-bg:rgba(255,255,255,0.24);z-index:1}@media (max-width:200px),(max-height:250px){viewer-toolbar{display:none}}#bottom{display:flex;justify-content:center}#sidenav-container{border-inline-end:1px solid var(--viewer-border-color);overflow:hidden;transition:transform 250ms cubic-bezier(.6,0,0,1),visibility 250ms;visibility:visible;width:var(--viewer-pdf-sidenav-width)}#sidenav-container.floating{bottom:0;position:absolute;top:0;z-index:1}#sidenav-container[closed]{transform:translateX(-100%);transition:transform 200ms cubic-bezier(.6,0,0,1),visibility 200ms,width 0ms 200ms;visibility:hidden;width:0}:host-context([dir='rtl']) #sidenav-container[closed]{transform:translateX(100%)}@media (max-width:500px),(max-height:250px){#sidenav-container{display:none}}#content-focus-rectangle{border:2px solid var(--google-grey-500);border-radius:2px;box-sizing:border-box;height:100%;pointer-events:none;position:absolute;top:0;width:100%}viewer-ink-host{height:100%;position:absolute;width:100%}#container{display:flex;flex:1;overflow:hidden;position:relative}#plugin{position:initial}#content{height:100%;left:0;position:sticky;top:0;user-select:none;z-index:initial}#sizer{top:0;width:100%;z-index:initial}#main{flex:1;overflow:hidden;position:relative}#scroller{direction:ltr;height:100%;overflow:auto;position:relative}#scroller:fullscreen{overflow:hidden}.spinner{mask-image:url(chrome://resources/images/throbber_small.svg);margin-inline-end:8px;--cr-spinner-size:16px}#searchifyProgress{--cr-toast-background:rgb(227,227,227);--cr-toast-text-color:rgb(31,31,31)}ink-text-annotations{height:calc(100% - var(--horizontal-scrollbar-width,0px));width:calc(100% - var(--vertical-scrollbar-width,0px))}
`])
}
function getHtml() {
    return html`<!--_html_template_start_--><!-- #html_wrapper_imports_start

import {AnnotationMode} from './constants.js';

#html_wrapper_imports_end -->

<viewer-toolbar id="toolbar"
    .docTitle="${this.title_}" .docLength="${this.docLength_}"
    .embeddedViewer="${this.embedded_}" .pageNo="${this.pageNo_}"
    .loadProgress="${this.loadProgress_}" .hasEdits="${this.hasEdits_}"
    .strings="${this.strings}"

    .annotationMode="${this.annotationMode_}"
    .enableUndoRedo="${!this.isTextboxActive_()}"
    .hasInk2Edits="${this.hasInk2AnnotationEdits_()}"

    .rotated="${this.isRotated_()}"
    .formFieldFocus="${this.formFieldFocus_}"
    .sidenavCollapsed="${this.sidenavCollapsed_}"
    .twoUpViewEnabled="${this.twoUpViewEnabled_}"
    .viewportZoom="${this.viewportZoom_}"
    .zoomBounds="${this.zoomBounds_}"

    .annotationAvailable="${this.annotationAvailable_()}"
    .pdfInk2Enabled="${this.pdfInk2Enabled_}"


    .pdfSaveToDriveEnabled="${this.pdfSaveToDriveEnabled_}"
    .saveToDriveProgress="${this.getSaveToDriveProgress_()}"
    .saveToDriveState="${this.saveToDriveState_}"

    @change-page="${this.onChangePage_}"
    @display-annotations-changed="${this.onDisplayAnnotationsChanged_}"
    @fit-to-changed="${this.onFitToChanged}"
    @glic-summarize="${this.onGlicSummarize_}"
    @present-click="${this.onPresentClick_}"
    @properties-click="${this.onPropertiesClick_}"
    @sidenav-toggle-click="${this.onSidenavToggleClick_}"
    @two-up-view-changed="${this.onTwoUpViewChanged_}"
    @zoom-changed="${this.onZoomChanged}" @zoom-in="${this.onZoomIn}"
    @zoom-out="${this.onZoomOut}" @rotate-left="${this.onRotateLeft_}"

    @annotation-mode-updated="${this.onAnnotationModeUpdated_}"

    @print="${this.onPrint_}" @save="${this.onToolbarSave_}"

    @save-to-drive="${this.onSaveToDrive_}"

    hidden>
</viewer-toolbar>

<div id="container">
  <div id="sidenav-container" ?closed="${this.sidenavCollapsed_}"
      ?hidden="${!this.toolbarEnabled_}">
    <viewer-pdf-sidenav id="sidenav"
        .activePage="${this.pageNo_}" .attachments="${this.attachments_}"
        .bookmarks="${this.bookmarks_}"
        .clockwiseRotations="${this.clockwiseRotations_}"
        .docLength="${this.docLength_}"
        .strings="${this.strings}"
        @change-page="${this.onChangePage_}"
        @change-page-and-xy="${this.onChangePageAndXy_}"
        @navigate="${this.onNavigate_}"
        @save-attachment="${this.onSaveAttachment_}">
    </viewer-pdf-sidenav>
  </div>
  <div id="main">
    <div id="scroller">
      <div id="sizer">
      </div>
      
        ${this.isInTextAnnotationMode_() ? html`
          <ink-text-annotations .viewport="${this.viewport}"
              @state-changed="${this.onTextBoxStateChanged_}">
          </ink-text-annotations>` : ""}
      
      <div id="content">
      </div>
    </div>
    <div id="content-focus-rectangle" ?hidden="${!this.documentHasFocus_}">
    </div>
    
      ${this.shouldShowInkBottomToolbar_() ? html`
        <cr-page-selector id="bottom" attr-for-selected="toolbar-name"
            selected="${this.annotationMode_}">
          <viewer-bottom-toolbar .strings="${this.strings}"
              toolbar-name="${AnnotationMode.DRAW}">
          </viewer-bottom-toolbar>
          <viewer-text-bottom-toolbar toolbar-name="${AnnotationMode.TEXT}">
          </viewer-text-bottom-toolbar>
        </cr-page-selector>` : ""}
    
  </div>
  
    ${this.shouldShowInkSidePanel_() ? html`
      <cr-page-selector attr-for-selected="page-name" id="side-panel"
          selected="${this.annotationMode_}">
        <viewer-side-panel page-name="${AnnotationMode.DRAW}">
        </viewer-side-panel>
        <viewer-text-side-panel page-name="${AnnotationMode.TEXT}">
        </viewer-text-side-panel>
      </cr-page-selector>
    ` : ""}
  
  <cr-toast id="searchifyProgress">
    <div class="spinner"></div>
    <span>Extracting text from PDF…</span>
  </cr-toast>
</div>

${this.showErrorDialog ? html`<viewer-error-dialog id="error-dialog">
</viewer-error-dialog>` : ""}

${this.showPasswordDialog_ ? html`<viewer-password-dialog id="password-dialog"
    @close="${this.onPasswordDialogClose_}"
    @password-submitted="${this.onPasswordSubmitted_}">
</viewer-password-dialog>` : ""}

${this.showPropertiesDialog_ ? html`<viewer-properties-dialog
    id="properties-dialog"
    .documentMetadata="${this.documentMetadata_}"
    .fileName="${this.fileName_}"
    .pageCount="${this.docLength_}"
    .strings="${this.strings}"
    @close="${this.onPropertiesDialogClose_}">
</viewer-properties-dialog>` : ""}


${this.pdfSaveToDriveEnabled_ ? html`<viewer-save-to-drive-bubble
    .docTitle="${this.title_}"
    .progress="${this.saveToDriveProgress_}"
    .state="${this.saveToDriveState_}"
    @save-to-drive-bubble-action="${this.onSaveToDriveBubbleAction_}">
</viewer-save-to-drive-bubble>` : ""}

<!--_html_template_end_-->`
}
const SaveRequestType$1 = chrome.pdfViewerPrivate.SaveRequestType;
var SaveToDriveBubbleAction;
(function(SaveToDriveBubbleAction) {
    SaveToDriveBubbleAction[SaveToDriveBubbleAction["ACTION"] = 0] = "ACTION";
    SaveToDriveBubbleAction[SaveToDriveBubbleAction["CANCEL_UPLOAD"] = 1] = "CANCEL_UPLOAD";
    SaveToDriveBubbleAction[SaveToDriveBubbleAction["MANAGE_STORAGE"] = 2] = "MANAGE_STORAGE";
    SaveToDriveBubbleAction[SaveToDriveBubbleAction["OPEN_IN_DRIVE"] = 3] = "OPEN_IN_DRIVE";
    SaveToDriveBubbleAction[SaveToDriveBubbleAction["RETRY"] = 4] = "RETRY";
    SaveToDriveBubbleAction[SaveToDriveBubbleAction["CLOSE"] = 5] = "CLOSE";
    SaveToDriveBubbleAction[SaveToDriveBubbleAction["COUNT"] = 6] = "COUNT"
}
)(SaveToDriveBubbleAction || (SaveToDriveBubbleAction = {}));
var SaveToDriveBubbleState;
(function(SaveToDriveBubbleState) {
    SaveToDriveBubbleState[SaveToDriveBubbleState["SHOW_BUBBLE"] = 0] = "SHOW_BUBBLE";
    SaveToDriveBubbleState[SaveToDriveBubbleState["SHOW_BUBBLE_UPLOADING_STATE"] = 1] = "SHOW_BUBBLE_UPLOADING_STATE";
    SaveToDriveBubbleState[SaveToDriveBubbleState["SHOW_BUBBLE_SUCCESS_STATE"] = 2] = "SHOW_BUBBLE_SUCCESS_STATE";
    SaveToDriveBubbleState[SaveToDriveBubbleState["SHOW_BUBBLE_CONNECTION_ERROR_STATE"] = 3] = "SHOW_BUBBLE_CONNECTION_ERROR_STATE";
    SaveToDriveBubbleState[SaveToDriveBubbleState["SHOW_BUBBLE_STORAGE_FULL_ERROR_STATE"] = 4] = "SHOW_BUBBLE_STORAGE_FULL_ERROR_STATE";
    SaveToDriveBubbleState[SaveToDriveBubbleState["SHOW_BUBBLE_SESSION_TIMEOUT_ERROR_STATE"] = 5] = "SHOW_BUBBLE_SESSION_TIMEOUT_ERROR_STATE";
    SaveToDriveBubbleState[SaveToDriveBubbleState["SHOW_BUBBLE_UNKNOWN_ERROR_STATE"] = 6] = "SHOW_BUBBLE_UNKNOWN_ERROR_STATE";
    SaveToDriveBubbleState[SaveToDriveBubbleState["COUNT"] = 7] = "COUNT"
}
)(SaveToDriveBubbleState || (SaveToDriveBubbleState = {}));
var SaveToDriveSaveType;
(function(SaveToDriveSaveType) {
    SaveToDriveSaveType[SaveToDriveSaveType["SAVE"] = 0] = "SAVE";
    SaveToDriveSaveType[SaveToDriveSaveType["SAVE_ORIGINAL_ONLY"] = 1] = "SAVE_ORIGINAL_ONLY";
    SaveToDriveSaveType[SaveToDriveSaveType["SAVE_ORIGINAL"] = 2] = "SAVE_ORIGINAL";
    SaveToDriveSaveType[SaveToDriveSaveType["SAVE_EDITED"] = 3] = "SAVE_EDITED";
    SaveToDriveSaveType[SaveToDriveSaveType["SAVE_WITH_ANNOTATION"] = 4] = "SAVE_WITH_ANNOTATION";
    SaveToDriveSaveType[SaveToDriveSaveType["COUNT"] = 5] = "COUNT"
}
)(SaveToDriveSaveType || (SaveToDriveSaveType = {}));
function recordSaveToDriveBubbleAction(action) {
    recordEnumeration("PDF.SaveToDrive.BubbleAction", action, SaveToDriveBubbleAction.COUNT)
}
function recordSaveToDriveBubbleState(bubbleState) {
    recordEnumeration("PDF.SaveToDrive.BubbleState", bubbleState, SaveToDriveBubbleState.COUNT)
}
function recordSaveToDriveRetrySaveType(retrySaveType) {
    recordEnumeration("PDF.SaveToDrive.RetrySaveType", retrySaveType, SaveToDriveSaveType.COUNT)
}
function recordSaveToDriveSaveType(saveToDriveSaveType) {
    recordEnumeration("PDF.SaveToDrive.SaveType", saveToDriveSaveType, SaveToDriveSaveType.COUNT)
}
function recordSaveToDriveBubbleActionMetrics(requestType) {
    recordSaveToDriveBubbleAction(SaveToDriveBubbleAction.ACTION);
    switch (requestType) {
    case SaveToDriveBubbleRequestType.CANCEL_UPLOAD:
        recordSaveToDriveBubbleAction(SaveToDriveBubbleAction.CANCEL_UPLOAD);
        break;
    case SaveToDriveBubbleRequestType.MANAGE_STORAGE:
        recordSaveToDriveBubbleAction(SaveToDriveBubbleAction.MANAGE_STORAGE);
        break;
    case SaveToDriveBubbleRequestType.OPEN_IN_DRIVE:
        recordSaveToDriveBubbleAction(SaveToDriveBubbleAction.OPEN_IN_DRIVE);
        break;
    case SaveToDriveBubbleRequestType.RETRY:
        recordSaveToDriveBubbleAction(SaveToDriveBubbleAction.RETRY);
        break;
    case SaveToDriveBubbleRequestType.DIALOG_CLOSED:
        recordSaveToDriveBubbleAction(SaveToDriveBubbleAction.CLOSE);
        break;
    default:
        assertNotReached("Unknown save to Drive bubble action: " + requestType)
    }
}
function recordSaveToDriveBubbleRetryMetrics(requestType, hasCommittedEdits) {
    switch (requestType) {
    case SaveRequestType$1.ANNOTATION:
        recordSaveToDriveRetrySaveType(SaveToDriveSaveType.SAVE_WITH_ANNOTATION);
        break;
    case SaveRequestType$1.ORIGINAL:
        recordSaveToDriveRetrySaveType(hasCommittedEdits ? SaveToDriveSaveType.SAVE_ORIGINAL : SaveToDriveSaveType.SAVE_ORIGINAL_ONLY);
        break;
    case SaveRequestType$1.EDITED:
        recordSaveToDriveRetrySaveType(SaveToDriveSaveType.SAVE_EDITED);
        break;
    default:
        assertNotReached("Unknown save request type for Save to Drive: " + requestType)
    }
}
function recordShowSaveToDriveBubbleMetrics(saveToDriveState) {
    recordSaveToDriveBubbleState(SaveToDriveBubbleState.SHOW_BUBBLE);
    switch (saveToDriveState) {
    case SaveToDriveState.UPLOADING:
        recordSaveToDriveBubbleState(SaveToDriveBubbleState.SHOW_BUBBLE_UPLOADING_STATE);
        break;
    case SaveToDriveState.SUCCESS:
        recordSaveToDriveBubbleState(SaveToDriveBubbleState.SHOW_BUBBLE_SUCCESS_STATE);
        break;
    case SaveToDriveState.CONNECTION_ERROR:
        recordSaveToDriveBubbleState(SaveToDriveBubbleState.SHOW_BUBBLE_CONNECTION_ERROR_STATE);
        break;
    case SaveToDriveState.STORAGE_FULL_ERROR:
        recordSaveToDriveBubbleState(SaveToDriveBubbleState.SHOW_BUBBLE_STORAGE_FULL_ERROR_STATE);
        break;
    case SaveToDriveState.SESSION_TIMEOUT_ERROR:
        recordSaveToDriveBubbleState(SaveToDriveBubbleState.SHOW_BUBBLE_SESSION_TIMEOUT_ERROR_STATE);
        break;
    case SaveToDriveState.UNKNOWN_ERROR:
        recordSaveToDriveBubbleState(SaveToDriveBubbleState.SHOW_BUBBLE_UNKNOWN_ERROR_STATE);
        break;
    default:
        assertNotReached("Unknown state for showing save to Drive bubble: " + saveToDriveState)
    }
}
function recordSaveToDriveMetrics(requestType, hasCommittedEdits, pdfInk2Enabled) {
    recordSaveToDriveSaveType(SaveToDriveSaveType.SAVE);
    switch (requestType) {
    case SaveRequestType$1.ANNOTATION:
        if (pdfInk2Enabled) {
            record(UserAction.SAVE_WITH_INK2_ANNOTATION)
        }
        recordSaveToDriveSaveType(SaveToDriveSaveType.SAVE_WITH_ANNOTATION);
        break;
    case SaveRequestType$1.ORIGINAL:
        recordSaveToDriveSaveType(hasCommittedEdits ? SaveToDriveSaveType.SAVE_ORIGINAL : SaveToDriveSaveType.SAVE_ORIGINAL_ONLY);
        break;
    case SaveRequestType$1.EDITED:
        recordSaveToDriveSaveType(SaveToDriveSaveType.SAVE_EDITED);
        break;
    default:
        assertNotReached("Unknown save request type for Save to Drive: " + requestType)
    }
}
const SaveToDriveErrorType = chrome.pdfViewerPrivate.SaveToDriveErrorType;
const SaveToDriveStatus = chrome.pdfViewerPrivate.SaveToDriveStatus;
const SaveRequestType = chrome.pdfViewerPrivate.SaveRequestType;
function getFilenameFromURL(url) {
    const mainUrl = url.split(/#|\?/)[0] || "";
    const components = mainUrl.split(/\/|\\/);
    const filename = components[components.length - 1] || "";
    try {
        return decodeURIComponent(filename)
    } catch (e) {
        if (e instanceof URIError) {
            return filename
        }
        throw e
    }
}
function eventToPromise(event, target) {
    return new Promise((resolve => listenOnce(target, event, (_e => resolve()))))
}
function hasFixedCtrlModifierOnly(e) {
    return e.ctrlKey && !e.shiftKey && !e.altKey && !e.metaKey
}
function hasCtrlModifierMaybeWithShift(e) {
    let metaModifier = e.metaKey;
    return hasCtrlModifier(e) && !e.altKey && !metaModifier
}
const LOCAL_STORAGE_SIDENAV_COLLAPSED_KEY = "sidenavCollapsed";
const BACKGROUND_COLOR = 4280821800;
function isEditedSaveRequestType(requestType) {
    return requestType === SaveRequestType.ANNOTATION || requestType === SaveRequestType.EDITED
}
function convertNoErrorStatusToSaveToDriveState(status) {
    switch (status) {
    case SaveToDriveStatus.INITIATED:
    case SaveToDriveStatus.FETCH_OAUTH:
    case SaveToDriveStatus.FETCH_PARENT_FOLDER:
    case SaveToDriveStatus.UPLOAD_STARTED:
    case SaveToDriveStatus.UPLOAD_IN_PROGRESS:
        return SaveToDriveState.UPLOADING;
    case SaveToDriveStatus.UPLOAD_COMPLETED:
        return SaveToDriveState.SUCCESS;
    default:
        return SaveToDriveState.UNINITIALIZED
    }
}
function convertSaveToDriveProgressToSaveToDriveState(progress) {
    switch (progress.errorType) {
    case SaveToDriveErrorType.NO_ERROR:
        return convertNoErrorStatusToSaveToDriveState(progress.status);
    case SaveToDriveErrorType.UNKNOWN_ERROR:
        return SaveToDriveState.UNKNOWN_ERROR;
    case SaveToDriveErrorType.QUOTA_EXCEEDED:
        return SaveToDriveState.STORAGE_FULL_ERROR;
    case SaveToDriveErrorType.OFFLINE:
        return SaveToDriveState.CONNECTION_ERROR;
    case SaveToDriveErrorType.OAUTH_ERROR:
        return SaveToDriveState.SESSION_TIMEOUT_ERROR;
    case SaveToDriveErrorType.ACCOUNT_CHOOSER_CANCELED:
        return SaveToDriveState.UNINITIALIZED;
    case SaveToDriveErrorType.PARENT_FOLDER_SELECTION_FAILED:
        return SaveToDriveState.UNKNOWN_ERROR;
    default:
        assertNotReached()
    }
}
function saveToDriveStateIsFinalState(state) {
    switch (state) {
    case SaveToDriveState.SUCCESS:
    case SaveToDriveState.CONNECTION_ERROR:
    case SaveToDriveState.STORAGE_FULL_ERROR:
    case SaveToDriveState.SESSION_TIMEOUT_ERROR:
    case SaveToDriveState.UNKNOWN_ERROR:
        return true;
    default:
        return false
    }
}
class PdfViewerElement extends PdfViewerBaseElement {
    static get is() {
        return "pdf-viewer"
    }
    static get styles() {
        return getCss()
    }
    render() {
        return getHtml.bind(this)()
    }
    static get properties() {
        return {
            showErrorDialog: {
                type: Boolean
            },
            strings: {
                type: Object
            },
            annotationMode_: {
                type: String
            },
            attachments_: {
                type: Array
            },
            bookmarks_: {
                type: Array
            },
            canSerializeDocument_: {
                type: Boolean
            },
            clockwiseRotations_: {
                type: Number
            },
            docLength_: {
                type: Number
            },
            documentHasFocus_: {
                type: Boolean
            },
            documentMetadata_: {
                type: Object
            },
            embedded_: {
                type: Boolean
            },
            fileName_: {
                type: String
            },
            hadPassword_: {
                type: Boolean
            },
            hasEdits_: {
                type: Boolean
            },
            hasCommittedInk2Edits_: {
                type: Boolean
            },
            formFieldFocus_: {
                type: String
            },
            loadProgress_: {
                type: Number
            },
            pageNo_: {
                type: Number
            },
            pdfInk2Enabled_: {
                type: Boolean
            },
            pdfTextAnnotationsEnabled_: {
                type: Boolean
            },
            pdfSaveToDriveEnabled_: {
                type: Boolean
            },
            saveToDriveProgress_: {
                type: Object
            },
            saveToDriveState_: {
                type: String
            },
            showPasswordDialog_: {
                type: Boolean
            },
            showPropertiesDialog_: {
                type: Boolean
            },
            sidenavCollapsed_: {
                type: Boolean
            },
            textboxState_: {
                type: Number
            },
            title_: {
                type: String
            },
            twoUpViewEnabled_: {
                type: Boolean
            },
            useSidePanelForInk_: {
                type: Boolean
            },
            viewportZoom_: {
                type: Number
            },
            zoomBounds_: {
                type: Object
            },
            toolbarEnabled_: {
                type: Boolean
            }
        }
    }
    beepCount = 0;
    #annotationMode__accessor_storage = AnnotationMode.OFF;
    get annotationMode_() {
        return this.#annotationMode__accessor_storage
    }
    set annotationMode_(value) {
        this.#annotationMode__accessor_storage = value
    }
    #attachments__accessor_storage = [];
    get attachments_() {
        return this.#attachments__accessor_storage
    }
    set attachments_(value) {
        this.#attachments__accessor_storage = value
    }
    #bookmarks__accessor_storage = [];
    get bookmarks_() {
        return this.#bookmarks__accessor_storage
    }
    set bookmarks_(value) {
        this.#bookmarks__accessor_storage = value
    }
    #canSerializeDocument__accessor_storage = false;
    get canSerializeDocument_() {
        return this.#canSerializeDocument__accessor_storage
    }
    set canSerializeDocument_(value) {
        this.#canSerializeDocument__accessor_storage = value
    }
    caretBrowsingEnabled_ = false;
    #clockwiseRotations__accessor_storage = 0;
    get clockwiseRotations_() {
        return this.#clockwiseRotations__accessor_storage
    }
    set clockwiseRotations_(value) {
        this.#clockwiseRotations__accessor_storage = value
    }
    #docLength__accessor_storage = 0;
    get docLength_() {
        return this.#docLength__accessor_storage
    }
    set docLength_(value) {
        this.#docLength__accessor_storage = value
    }
    #documentHasFocus__accessor_storage = false;
    get documentHasFocus_() {
        return this.#documentHasFocus__accessor_storage
    }
    set documentHasFocus_(value) {
        this.#documentHasFocus__accessor_storage = value
    }
    #documentMetadata__accessor_storage = {
        author: "",
        canSerializeDocument: false,
        creationDate: "",
        creator: "",
        fileSize: "",
        keywords: "",
        linearized: false,
        modDate: "",
        pageSize: "",
        producer: "",
        subject: "",
        title: "",
        version: ""
    };
    get documentMetadata_() {
        return this.#documentMetadata__accessor_storage
    }
    set documentMetadata_(value) {
        this.#documentMetadata__accessor_storage = value
    }
    #embedded__accessor_storage = false;
    get embedded_() {
        return this.#embedded__accessor_storage
    }
    set embedded_(value) {
        this.#embedded__accessor_storage = value
    }
    #fileName__accessor_storage = "";
    get fileName_() {
        return this.#fileName__accessor_storage
    }
    set fileName_(value) {
        this.#fileName__accessor_storage = value
    }
    #hadPassword__accessor_storage = false;
    get hadPassword_() {
        return this.#hadPassword__accessor_storage
    }
    set hadPassword_(value) {
        this.#hadPassword__accessor_storage = value
    }
    #hasEdits__accessor_storage = false;
    get hasEdits_() {
        return this.#hasEdits__accessor_storage
    }
    set hasEdits_(value) {
        this.#hasEdits__accessor_storage = value
    }
    #hasCommittedInk2Edits__accessor_storage = false;
    get hasCommittedInk2Edits_() {
        return this.#hasCommittedInk2Edits__accessor_storage
    }
    set hasCommittedInk2Edits_(value) {
        this.#hasCommittedInk2Edits__accessor_storage = value
    }
    hasUnsavedEdits_ = false;
    #formFieldFocus__accessor_storage = FormFieldFocusType.NONE;
    get formFieldFocus_() {
        return this.#formFieldFocus__accessor_storage
    }
    set formFieldFocus_(value) {
        this.#formFieldFocus__accessor_storage = value
    }
    #loadProgress__accessor_storage = 0;
    get loadProgress_() {
        return this.#loadProgress__accessor_storage
    }
    set loadProgress_(value) {
        this.#loadProgress__accessor_storage = value
    }
    navigator_ = null;
    #pageNo__accessor_storage = 0;
    get pageNo_() {
        return this.#pageNo__accessor_storage
    }
    set pageNo_(value) {
        this.#pageNo__accessor_storage = value
    }
    pdfGetSaveDataInBlocks_ = false;
    #pdfInk2Enabled__accessor_storage = false;
    get pdfInk2Enabled_() {
        return this.#pdfInk2Enabled__accessor_storage
    }
    set pdfInk2Enabled_(value) {
        this.#pdfInk2Enabled__accessor_storage = value
    }
    #pdfTextAnnotationsEnabled__accessor_storage = false;
    get pdfTextAnnotationsEnabled_() {
        return this.#pdfTextAnnotationsEnabled__accessor_storage
    }
    set pdfTextAnnotationsEnabled_(value) {
        this.#pdfTextAnnotationsEnabled__accessor_storage = value
    }
    #pdfSaveToDriveEnabled__accessor_storage = false;
    get pdfSaveToDriveEnabled_() {
        return this.#pdfSaveToDriveEnabled__accessor_storage
    }
    set pdfSaveToDriveEnabled_(value) {
        this.#pdfSaveToDriveEnabled__accessor_storage = value
    }
    #saveToDriveProgress__accessor_storage = {
        status: SaveToDriveStatus.NOT_STARTED,
        errorType: SaveToDriveErrorType.NO_ERROR
    };
    get saveToDriveProgress_() {
        return this.#saveToDriveProgress__accessor_storage
    }
    set saveToDriveProgress_(value) {
        this.#saveToDriveProgress__accessor_storage = value
    }
    #saveToDriveState__accessor_storage = SaveToDriveState.UNINITIALIZED;
    get saveToDriveState_() {
        return this.#saveToDriveState__accessor_storage
    }
    set saveToDriveState_(value) {
        this.#saveToDriveState__accessor_storage = value
    }
    saveToDriveRequestType_ = SaveRequestType.ORIGINAL;
    pdfSearchifySaveEnabled_ = false;
    pdfUseShowSaveFilePicker_ = false;
    pluginController_ = PluginController.getInstance();
    restoreAnnotationMode_ = AnnotationMode.OFF;
    showBeforeUnloadDialog_ = false;
    #showPasswordDialog__accessor_storage = false;
    get showPasswordDialog_() {
        return this.#showPasswordDialog__accessor_storage
    }
    set showPasswordDialog_(value) {
        this.#showPasswordDialog__accessor_storage = value
    }
    #showPropertiesDialog__accessor_storage = false;
    get showPropertiesDialog_() {
        return this.#showPropertiesDialog__accessor_storage
    }
    set showPropertiesDialog_(value) {
        this.#showPropertiesDialog__accessor_storage = value
    }
    #sidenavCollapsed__accessor_storage;
    get sidenavCollapsed_() {
        return this.#sidenavCollapsed__accessor_storage
    }
    set sidenavCollapsed_(value) {
        this.#sidenavCollapsed__accessor_storage = value
    }
    #textboxState__accessor_storage = TextBoxState.INACTIVE;
    get textboxState_() {
        return this.#textboxState__accessor_storage
    }
    set textboxState_(value) {
        this.#textboxState__accessor_storage = value
    }
    #title__accessor_storage = "";
    get title_() {
        return this.#title__accessor_storage
    }
    set title_(value) {
        this.#title__accessor_storage = value
    }
    #toolbarEnabled__accessor_storage = false;
    get toolbarEnabled_() {
        return this.#toolbarEnabled__accessor_storage
    }
    set toolbarEnabled_(value) {
        this.#toolbarEnabled__accessor_storage = value
    }
    #twoUpViewEnabled__accessor_storage = false;
    get twoUpViewEnabled_() {
        return this.#twoUpViewEnabled__accessor_storage
    }
    set twoUpViewEnabled_(value) {
        this.#twoUpViewEnabled__accessor_storage = value
    }
    #useSidePanelForInk__accessor_storage = false;
    get useSidePanelForInk_() {
        return this.#useSidePanelForInk__accessor_storage
    }
    set useSidePanelForInk_(value) {
        this.#useSidePanelForInk__accessor_storage = value
    }
    #viewportZoom__accessor_storage = 1;
    get viewportZoom_() {
        return this.#viewportZoom__accessor_storage
    }
    set viewportZoom_(value) {
        this.#viewportZoom__accessor_storage = value
    }
    #zoomBounds__accessor_storage = {
        min: 0,
        max: 0
    };
    get zoomBounds_() {
        return this.#zoomBounds__accessor_storage
    }
    set zoomBounds_(value) {
        this.#zoomBounds__accessor_storage = value
    }
    hasSearchifyText_ = false;
    constructor() {
        PdfHelpBubbleProxyImpl.createConnectedInstance();
        super();
        this.sidenavCollapsed_ = Boolean(Number.parseInt(LocalStorageProxyImpl.getInstance().getItem(LOCAL_STORAGE_SIDENAV_COLLAPSED_KEY), 10))
    }
    willUpdate(changedProperties) {
        super.willUpdate(changedProperties);
        const changedPrivateProperties = changedProperties;
        if (changedPrivateProperties.has("pdfInk2Enabled_") && this.pdfInk2Enabled_) {
            Ink2Manager.getInstance().setViewport(this.viewport)
        }
    }
    updated(changedProperties) {
        super.updated(changedProperties);
        if (changedProperties.has("showErrorDialog") && this.showErrorDialog) {
            this.onErrorDialog_()
        }
        const changedPrivateProperties = changedProperties;
        if (changedPrivateProperties.has("saveToDriveState_")) {
            this.onSaveToDriveStateChanged_(changedPrivateProperties.get("saveToDriveState_"))
        }
    }
    connectedCallback() {
        super.connectedCallback();
        this.tracker.add(window, "beforeunload", this.onBeforeUnload_.bind(this));
        const mediaQuery = window.matchMedia("(min-width: 960px)");
        this.useSidePanelForInk_ = mediaQuery.matches;
        this.tracker.add(mediaQuery, "change", ( () => {
            this.useSidePanelForInk_ = mediaQuery.matches;
            if (this.annotationMode_ !== AnnotationMode.OFF) {
                record(this.useSidePanelForInk_ ? UserAction.OPEN_INK2_SIDE_PANEL : UserAction.OPEN_INK2_BOTTOM_TOOLBAR)
            }
        }
        ));
        this.tracker.add(Ink2Manager.getInstance(), "undo-redo-state-changed", this.handleUndoRedoStateChanged_.bind(this))
    }
    disconnectedCallback() {
        this.tracker.removeAll();
        super.disconnectedCallback()
    }
    getBackgroundColor() {
        return BACKGROUND_COLOR
    }
    setPluginSrc(plugin) {
        plugin.src = this.browserApi.getStreamInfo().streamUrl
    }
    init(browserApi) {
        this.initInternal(browserApi, this.$.scroller, this.$.sizer, this.$.content);
        this.fileName_ = getFilenameFromURL(this.originalUrl);
        this.title_ = this.fileName_;
        assert(this.paramsParser);
        this.toolbarEnabled_ = this.paramsParser.shouldShowToolbar(this.originalUrl);
        if (this.toolbarEnabled_) {
            this.$.toolbar.hidden = false
        }
        const showSidenav = this.paramsParser.shouldShowSidenav(this.originalUrl, this.sidenavCollapsed_);
        this.sidenavCollapsed_ = !showSidenav;
        this.navigator_ = new PdfNavigatorImpl(this.originalUrl,this.viewport,this.paramsParser,new NavigatorDelegateImpl(browserApi));
        if (this.pdfOopifEnabled) {
            chrome.pdfViewerPrivate.onSave.addListener(this.onSave_.bind(this))
        } else {
            chrome.mimeHandlerPrivate.onSave.addListener(this.onSave_.bind(this))
        }
        chrome.pdfViewerPrivate.onShouldUpdateViewport.addListener(this.handleMaybeUpdateViewport_.bind(this));
        PdfViewerPrivateProxyImpl.getInstance().onSaveToDriveProgress.addListener(this.handleSaveToDriveProgress_.bind(this));
        this.embedded_ = this.browserApi.getStreamInfo().embedded;
        if (this.pdfOopifEnabled && !this.embedded_) {
            window.focus()
        }
    }
    handleKeyEvent(e) {
        if (shouldIgnoreKeyEvents() || e.defaultPrevented) {
            return
        }
        if (this.viewport.handleDirectionalKeyEvent(e, this.formFieldFocus_ !== FormFieldFocusType.NONE, this.caretBrowsingEnabled_)) {
            return
        }
        if (document.fullscreenElement !== null) {
            if (hasCtrlModifier(e) && (e.key === "=" || e.key === "-" || e.key === "+")) {
                e.preventDefault()
            }
            return
        }
        if (this.isInTextAnnotationMode_()) {
            const textStyle = getTextStyleForShortcut(e);
            if (textStyle !== null) {
                e.preventDefault();
                Ink2Manager.getInstance().toggleTextStyle(textStyle);
                return
            }
        }
        switch (e.key) {
        case "a":
            if (hasCtrlModifierOnly(e)) {
                this.pluginController_.selectAll();
                e.preventDefault()
            }
            return;
        case "Enter":
            if (e.fromPlugin && this.isInTextAnnotationMode_()) {
                this.maybeCreateTextAnnotation_()
            }
            return;
        case "v":
            if (e.fromPlugin && hasCtrlModifierOnly(e) && this.isInTextAnnotationMode_()) {
                this.maybePasteTextAnnotation_()
            }
            return
        }
        this.handleToolbarKeyEvent_(e)
    }
    maybePasteTextAnnotation_() {
        const focused = this.shadowRoot.activeElement;
        if (!!focused && !this.$.scroller.contains(focused)) {
            return
        }
        const annotations = this.shadowRoot.querySelector("ink-text-annotations");
        assert(annotations);
        annotations.pasteAnnotation()
    }
    handleToolbarKeyEvent_(e) {
        switch (e.key) {
        case "[":
            if (hasFixedCtrlModifierOnly(e)) {
                this.rotateCounterclockwise()
            }
            return;
        case "\\":
            if (hasFixedCtrlModifierOnly(e)) {
                this.$.toolbar.fitToggle()
            }
            return;
        case "]":
            if (hasFixedCtrlModifierOnly(e)) {
                this.rotateClockwise()
            }
            return;
        case "z":
        case "Z":
            if (hasCtrlModifierMaybeWithShift(e)) {
                if (e.shiftKey) {
                    this.$.toolbar.redo()
                } else {
                    this.$.toolbar.undo()
                }
            }
            return;
        case "y":
        case "Y":
            if (hasCtrlModifierOnly(e)) {
                this.$.toolbar.redo()
            }
            return
        }
    }
    async maybeCreateTextAnnotation_(location) {
        const hasActive = this.isTextboxActive_();
        if (hasActive) {
            await this.maybeCommitActiveTextbox_()
        }
        Ink2Manager.getInstance().initializeTextAnnotation(location, hasActive)
    }
    recordEnterExitAnnotationModeMetrics_(newAnnotationMode) {
        switch (this.annotationMode_) {
        case AnnotationMode.DRAW:
            record(UserAction.EXIT_INK2_ANNOTATION_MODE);
            break;
        case AnnotationMode.TEXT:
            record(UserAction.EXIT_INK2_TEXT_ANNOTATION_MODE);
            break;
        case AnnotationMode.OFF:
            break;
        default:
            assertNotReached()
        }
        switch (newAnnotationMode) {
        case AnnotationMode.DRAW:
            record(UserAction.ENTER_INK2_ANNOTATION_MODE);
            break;
        case AnnotationMode.TEXT:
            record(UserAction.ENTER_INK2_TEXT_ANNOTATION_MODE);
            break;
        case AnnotationMode.OFF:
            break;
        default:
            assertNotReached()
        }
    }
    onAnnotationModeUpdated_(e) {
        this.setAnnotationMode_(e.detail)
    }
    async setAnnotationMode_(newAnnotationMode) {
        assert(this.pdfInk2Enabled_);
        if (newAnnotationMode === this.annotationMode_) {
            return
        }
        if (this.annotationMode_ === AnnotationMode.TEXT) {
            await this.maybeCommitActiveTextbox_()
        }
        if (this.annotationMode_ === AnnotationMode.OFF) {
            record(this.useSidePanelForInk_ ? UserAction.OPEN_INK2_SIDE_PANEL : UserAction.OPEN_INK2_BOTTOM_TOOLBAR)
        }
        if (this.restoreAnnotationMode_ === AnnotationMode.OFF) {
            this.recordEnterExitAnnotationModeMetrics_(newAnnotationMode)
        }
        this.pluginController_.setAnnotationMode(newAnnotationMode);
        if (newAnnotationMode === AnnotationMode.DRAW && !Ink2Manager.getInstance().isInitializationStarted()) {
            await Ink2Manager.getInstance().initializeBrush()
        }
        if (newAnnotationMode === AnnotationMode.TEXT && !Ink2Manager.getInstance().isTextInitializationComplete()) {
            await Ink2Manager.getInstance().initializeTextAnnotations()
        }
        this.annotationMode_ = newAnnotationMode
    }
    onDisplayAnnotationsChanged_(e) {
        assert(this.currentController);
        this.currentController.setDisplayAnnotations(e.detail)
    }
    async enterPresentationMode_() {
        const scroller = this.$.scroller;
        this.viewport.saveZoomState();
        const fullscreenPromise = Promise.all([eventToPromise("fullscreenchange", scroller), scroller.requestFullscreen()]);
        if (this.pdfInk2Enabled_ && this.annotationMode_ !== AnnotationMode.OFF) {
            this.restoreAnnotationMode_ = this.annotationMode_;
            await this.setAnnotationMode_(AnnotationMode.OFF)
        }
        assert(this.annotationMode_ === AnnotationMode.OFF);
        await fullscreenPromise;
        this.forceFit(FittingType.FIT_TO_HEIGHT);
        this.viewport.setPresentationMode(true);
        this.pluginController_.setPresentationMode(true)
    }
    exitPresentationMode_() {
        assert(document.fullscreenElement === null);
        this.viewport.setPresentationMode(false);
        this.pluginController_.setPresentationMode(false);
        this.focusPlugin_();
        this.viewport.restoreZoomState()
    }
    async maybeRestoreAnnotationMode_() {
        if (this.restoreAnnotationMode_ !== AnnotationMode.OFF) {
            await this.setAnnotationMode_(this.restoreAnnotationMode_);
            assert(this.annotationMode_ !== AnnotationMode.OFF);
            this.restoreAnnotationMode_ = AnnotationMode.OFF
        }
    }
    focusPlugin_() {
        this.shadowRoot.querySelector("embed").focus();
        this.pluginController_.focus()
    }
    async onPresentClick_() {
        await this.enterPresentationMode_();
        await eventToPromise("fullscreenchange", this.$.scroller);
        this.exitPresentationMode_();
        await this.maybeRestoreAnnotationMode_()
    }
    onPropertiesClick_() {
        assert(!this.showPropertiesDialog_);
        this.showPropertiesDialog_ = true
    }
    onPropertiesDialogClose_() {
        assert(this.showPropertiesDialog_);
        this.showPropertiesDialog_ = false
    }
    onTwoUpViewChanged_(e) {
        const twoUpViewEnabled = e.detail;
        assert(this.currentController);
        this.currentController.setTwoUpView(twoUpViewEnabled);
        record(twoUpViewEnabled ? UserAction.TWO_UP_VIEW_ENABLE : UserAction.TWO_UP_VIEW_DISABLE)
    }
    goToPageAndXy_(origin, page, message) {
        this.viewport.goToPageAndXy(page, message.x, message.y);
        if (origin === ChangePageOrigin.BOOKMARK) {
            record(UserAction.FOLLOW_BOOKMARK)
        }
    }
    get bookmarks() {
        return this.bookmarks_
    }
    get pdfTitle() {
        return this.title_
    }
    setLoadState(loadState) {
        super.setLoadState(loadState);
        if (loadState === LoadState.FAILED) {
            this.closePasswordDialog_()
        }
    }
    updateProgress(progress) {
        if (this.toolbarEnabled_) {
            this.loadProgress_ = progress
        }
        super.updateProgress(progress);
        if (progress === 100) {
            this.maybeRenderTextDirectiveHighlights_(this.originalUrl)
        }
    }
    onErrorDialog_() {
        if (!chrome.tabs || this.browserApi.getStreamInfo().tabId === -1) {
            return
        }
        const errorDialog = this.shadowRoot.querySelector("#error-dialog");
        errorDialog.reloadFn = () => {
            chrome.tabs.reload(this.browserApi.getStreamInfo().tabId)
        }
    }
    closePasswordDialog_() {
        const passwordDialog = this.shadowRoot.querySelector("#password-dialog");
        if (passwordDialog) {
            passwordDialog.close()
        }
    }
    onPasswordDialogClose_() {
        this.showPasswordDialog_ = false
    }
    onPasswordSubmitted_(event) {
        this.pluginController_.getPasswordComplete(event.detail.password)
    }
    updateUiForViewportChange() {
        this.clockwiseRotations_ = this.viewport.getClockwiseRotations();
        this.pageNo_ = this.viewport.getMostVisiblePage() + 1;
        this.twoUpViewEnabled_ = this.viewport.twoUpViewEnabled();
        assert(this.currentController);
        this.currentController.viewportChanged();
        if (this.pdfInk2Enabled_) {
            const hasScrollbars = this.viewport.documentHasScrollbars();
            const scrollbarWidthStyle = `${this.viewport.scrollbarWidth}px`;
            this.style.setProperty("--vertical-scrollbar-width", hasScrollbars.vertical ? scrollbarWidthStyle : "0px");
            this.style.setProperty("--horizontal-scrollbar-width", hasScrollbars.horizontal ? scrollbarWidthStyle : "0px");
            const annotations = this.shadowRoot.querySelector("ink-text-annotations");
            if (annotations) {
                annotations.viewportChanged()
            }
        }
    }
    handleStrings(strings) {
        super.handleStrings(strings);
        this.pdfGetSaveDataInBlocks_ = loadTimeData.getBoolean("pdfGetSaveDataInBlocks");
        this.pdfInk2Enabled_ = loadTimeData.getBoolean("pdfInk2Enabled");
        this.pdfTextAnnotationsEnabled_ = loadTimeData.getBoolean("pdfTextAnnotationsEnabled");
        this.pdfSaveToDriveEnabled_ = loadTimeData.getBoolean("pdfSaveToDrive");
        this.pdfSearchifySaveEnabled_ = loadTimeData.getBoolean("pdfSearchifySaveEnabled");
        this.pdfUseShowSaveFilePicker_ = loadTimeData.getBoolean("pdfUseShowSaveFilePicker");
        const presetZoomFactors = this.viewport.presetZoomFactors;
        assert(presetZoomFactors.length > 0);
        this.zoomBounds_.min = Math.round(presetZoomFactors[0] * 100);
        this.zoomBounds_.max = Math.round(presetZoomFactors[presetZoomFactors.length - 1] * 100);
        const hasGlic = loadTimeData.getBoolean("pdfGlicSummarizeEnabled");
        if (hasGlic || this.pdfInk2Enabled_) {
            this.updateComplete.then(( () => {
                if (hasGlic) {
                    const summarizeBtn = this.$.toolbar.shadowRoot.querySelector("#glic-summarize-button");
                    if (summarizeBtn) {
                        this.registerHelpBubble("PdfHelpBubbleHandlerFactory::kPdfGlicSummarizeElementId", summarizeBtn)
                    }
                }
                if (this.pdfInk2Enabled_) {
                    this.registerHelpBubble("PdfHelpBubbleHandlerFactory::kPdfInkSignaturesDrawElementId", this.$.toolbar.shadowRoot.querySelector("#annotate"));
                    if (this.pdfTextAnnotationsEnabled_) {
                        this.registerHelpBubble("PdfHelpBubbleHandlerFactory::kPdfInkSignaturesAddTextElementId", this.$.toolbar.shadowRoot.querySelector("#text-annotate"))
                    }
                }
            }
            ))
        }
    }
    handleScriptingMessage(message) {
        if (super.handleScriptingMessage(message)) {
            return true
        }
        if (this.delayScriptingMessage(message)) {
            return true
        }
        let messageType;
        switch (message.data.type) {
        case "getSelectedText":
            messageType = PostMessageDataType.GET_SELECTED_TEXT;
            this.pluginController_.getSelectedText().then(this.handleSelectedTextReply.bind(this));
            break;
        case "print":
            messageType = PostMessageDataType.PRINT;
            this.maybeCommitActiveTextbox_().then(( () => {
                this.pluginController_.print()
            }
            ));
            break;
        case "selectAll":
            messageType = PostMessageDataType.SELECT_ALL;
            this.pluginController_.selectAll();
            break;
        default:
            return false
        }
        recordEnumeration("PDF.PostMessageDataType", messageType, PostMessageDataType.COUNT);
        return true
    }
    handlePluginMessage(e) {
        const data = e.detail;
        switch (data.type) {
        case "attachments":
            const attachmentsData = data;
            this.setAttachments_(attachmentsData.attachmentsData);
            return;
        case "beep":
            this.handleBeep_();
            return;
        case "bookmarks":
            const bookmarksData = data;
            this.setBookmarks_(bookmarksData.bookmarksData);
            return;
        case "documentDimensions":
            this.setDocumentDimensions(convertDocumentDimensionsMessage(data));
            return;
        case "documentFocusChanged":
            const hasFocusData = data;
            this.documentHasFocus_ = hasFocusData.hasFocus;
            return;
        case "email":
            const emailData = data;
            const href = "mailto:" + emailData.to + "?cc=" + emailData.cc + "&bcc=" + emailData.bcc + "&subject=" + emailData.subject + "&body=" + emailData.body;
            this.handleNavigate_(href, WindowOpenDisposition.CURRENT_TAB);
            return;
        case "executedEditCommand":
            const editCommandData = data;
            const editCommand = editCommandData.editCommand;
            switch (editCommand) {
            case "Cut":
                record(UserAction.CUT);
                return;
            case "Copy":
                record(UserAction.COPY);
                if (this.hasSearchifyText_) {
                    record(UserAction.COPY_SEARCHIFIED)
                }
                return;
            case "Paste":
                record(UserAction.PASTE);
                return;
            default:
                assertNotReached("Unknown executedEditCommand data received: " + editCommand)
            }
        case "finishInkStroke":
            const modifiedData = data;
            this.handleFinishInkStroke_(modifiedData.modified);
            return;
        case "formFocusChange":
            const focusedData = convertFormFocusChangeMessage(data);
            this.formFieldFocus_ = focusedData.focused;
            return;
        case "getPassword":
            this.handlePasswordRequest_();
            return;
        case "loadProgress":
            const progressData = convertLoadProgressMessage(data);
            this.updateProgress(progressData.progress);
            return;
        case "metadata":
            const metadataData = data;
            this.setDocumentMetadata_(metadataData.metadataData);
            return;
        case "navigate":
            const navigateData = data;
            this.handleNavigate_(navigateData.url, navigateData.disposition);
            return;
        case "rendererPreferencesUpdated":
            const caretBrowsingEnabledData = data;
            this.caretBrowsingEnabled_ = caretBrowsingEnabledData.caretBrowsingEnabled;
            return;
        case "sendClickEvent":
            if (this.annotationMode_ !== AnnotationMode.TEXT) {
                return
            }
            const location = data;
            if (this.viewport.isPointOnScrollbar(location)) {
                const annotations = this.shadowRoot.querySelector("ink-text-annotations");
                assert(annotations);
                annotations.blurActiveAnnotation()
            } else {
                this.maybeCreateTextAnnotation_(data)
            }
            return;
        case "sendKeyEvent":
            const keyEvent = convertSendKeyEventMessage(data);
            keyEvent.fromPlugin = true;
            this.handleKeyEvent(keyEvent);
            return;
        case "setIsEditing":
            this.hasEdits_ = true;
            return;
        case "setHasSearchifyText":
            this.hasSearchifyText_ = true;
            return;
        case "showSearchifyInProgress":
            if (data.show) {
                this.$.searchifyProgress.show()
            } else {
                this.$.searchifyProgress.hide()
            }
            return;
        case "startInkStroke":
            this.handleStartInkStroke_();
            return;
        case "startedFindInPage":
            record(UserAction.FIND_IN_PAGE);
            if (this.hasSearchifyText_) {
                record(UserAction.FIND_IN_PAGE_SEARCHIFIED)
            }
            return;
        case "touchSelectionOccurred":
            this.sendScriptingMessage({
                type: "touchSelectionOccurred"
            });
            return;
        case "updateThumbnail":
            const thumbnailData = data;
            this.pluginController_.getEventTarget().dispatchEvent(new CustomEvent(PluginControllerEventType.UPDATE_THUMBNAIL,{
                detail: thumbnailData
            }));
            return;
        default:
            assertNotReached("Unknown message type received: " + data.type)
        }
    }
    forceFit(view) {
        this.$.toolbar.forceFit(view)
    }
    afterZoom(viewportZoom) {
        this.viewportZoom_ = viewportZoom
    }
    setDocumentDimensions(documentDimensions) {
        super.setDocumentDimensions(documentDimensions);
        this.closePasswordDialog_();
        if (this.toolbarEnabled_) {
            this.docLength_ = this.documentDimensions.pageDimensions.length
        }
    }
    handleBeep_() {
        this.beepCount += 1
    }
    handlePasswordRequest_() {
        if (!this.showPasswordDialog_) {
            this.hadPassword_ = true;
            this.showPasswordDialog_ = true;
            this.sendScriptingMessage({
                type: "passwordPrompted"
            })
        } else {
            const passwordDialog = this.shadowRoot.querySelector("#password-dialog");
            assert(passwordDialog);
            passwordDialog.deny()
        }
    }
    handleNavigate_(url, disposition) {
        this.navigator_.navigate(url, disposition)
    }
    handleSaveToDriveProgress_(streamUrl, progress) {
        if (streamUrl !== this.browserApi.getStreamInfo().streamUrl) {
            return
        }
        this.saveToDriveProgress_ = progress;
        this.saveToDriveState_ = convertSaveToDriveProgressToSaveToDriveState(progress)
    }
    handleMaybeUpdateViewport_(newUrl) {
        assert(this.paramsParser);
        this.paramsParser.getViewportFromUrlParams(newUrl).then((params => this.handleUrlParams(params)));
        this.maybeRenderTextDirectiveHighlights_(newUrl)
    }
    handleStartInkStroke_() {
        this.pluginController_.getEventTarget().dispatchEvent(new CustomEvent(PluginControllerEventType.START_INK_STROKE))
    }
    handleFinishInkStroke_(modified) {
        if (modified) {
            this.hasCommittedInk2Edits_ = true;
            this.hasUnsavedEdits_ = true;
            this.setShowBeforeUnloadDialog_(true)
        }
        this.pluginController_.getEventTarget().dispatchEvent(new CustomEvent(PluginControllerEventType.FINISH_INK_STROKE,{
            detail: modified
        }))
    }
    hasCommittedEdits_() {
        let hasEdits = this.hasEdits_;
        hasEdits ||= this.hasCommittedInk2Edits_;
        return hasEdits
    }
    setAttachments_(attachments) {
        this.attachments_ = attachments
    }
    setBookmarks_(bookmarks) {
        this.bookmarks_ = bookmarks
    }
    setDocumentMetadata_(metadata) {
        this.documentMetadata_ = metadata;
        this.title_ = this.documentMetadata_.title || this.fileName_;
        if (this.pdfOopifEnabled && !this.embedded_) {
            PdfViewerPrivateProxyImpl.getInstance().setPdfDocumentTitle(this.title_)
        } else {
            document.title = this.title_
        }
        this.canSerializeDocument_ = this.documentMetadata_.canSerializeDocument
    }
    async onSaveAttachment_(e) {
        const index = e.detail;
        assert(this.attachments_[index] !== undefined);
        const size = this.attachments_[index].size;
        assert(size !== -1);
        let dataArray = [];
        if (size !== 0) {
            assert(this.currentController);
            const result = await this.currentController.saveAttachment(index);
            const MAX_FILE_SIZE = 100 * 1e3 * 1e3;
            const bufView = new Uint8Array(result.dataToSave);
            assert(bufView.length <= MAX_FILE_SIZE, `File too large to be saved: ${bufView.length} bytes.`);
            assert(bufView.length === size, `Received attachment size does not match its expected value: ${size} bytes.`);
            dataArray = [result.dataToSave]
        }
        const blob = new Blob(dataArray);
        const fileName = this.attachments_[index].name;
        if (this.pdfUseShowSaveFilePicker_) {
            try {
                const fileHandle = await window.showSaveFilePicker({
                    suggestedName: fileName
                });
                const writable = await fileHandle.createWritable();
                await writable.write(blob);
                await writable.close()
            } catch (error) {
                if (error instanceof Error && error.name !== "AbortError") {
                    console.error("window.showSaveFilePicker failed: " + error)
                }
            }
        } else {
            const writer = await this.selectFileAndGetWriter_(fileName);
            if (writer !== null) {
                writer.write(blob)
            }
        }
    }
    onSave_(streamUrl) {
        if (streamUrl !== this.browserApi.getStreamInfo().streamUrl) {
            return
        }
        let shouldSaveWithAnnotation = false;
        if (this.pdfInk2Enabled_) {
            shouldSaveWithAnnotation = this.hasCommittedInk2Edits_ || this.textboxState_ === TextBoxState.EDITED
        }
        let saveMode;
        if (shouldSaveWithAnnotation) {
            saveMode = SaveRequestType.ANNOTATION
        } else if (this.hasEdits_) {
            saveMode = SaveRequestType.EDITED
        } else if (this.hasSearchifyText_ && this.pdfSearchifySaveEnabled_) {
            saveMode = SaveRequestType.SEARCHIFIED
        } else {
            saveMode = SaveRequestType.ORIGINAL
        }
        this.save_(saveMode)
    }
    onToolbarSave_(e) {
        this.save_(e.detail)
    }
    getStreamUrlForTesting() {
        return this.browserApi.getStreamInfo().streamUrl
    }
    setOnSaveToDriveProgressListenerForTesting() {
        PdfViewerPrivateProxyImpl.getInstance().onSaveToDriveProgress.addListener(this.handleSaveToDriveProgress_.bind(this))
    }
    setPdfNavigatorForTesting(navigator) {
        this.navigator_ = navigator
    }
    getSaveToDriveProgress_() {
        if (!this.isSaveToDriveUploading_()) {
            return 0
        }
        const fileSizeBytes = this.saveToDriveProgress_.fileSizeBytes ?? 0;
        if (fileSizeBytes === 0) {
            return 0
        }
        const uploadedBytes = this.saveToDriveProgress_.uploadedBytes ?? 0;
        return Math.round(uploadedBytes / fileSizeBytes * 100)
    }
    isSaveToDriveUploading_() {
        return this.saveToDriveState_ === SaveToDriveState.UPLOADING
    }
    async onSaveToDrive_(e) {
        if (this.saveToDriveState_ === SaveToDriveState.UNINITIALIZED) {
            this.saveToDriveRequestType_ = e.detail;
            let pdfInk2Enabled = false;
            pdfInk2Enabled = this.pdfInk2Enabled_;
            if (this.pdfInk2Enabled_ && e.detail === SaveRequestType.ANNOTATION) {
                await this.maybeCommitActiveTextbox_();
                Ink2Manager.getInstance().initiateSave()
            }
            PdfViewerPrivateProxyImpl.getInstance().saveToDrive(e.detail);
            recordSaveToDriveMetrics(e.detail, this.hasCommittedEdits_(), pdfInk2Enabled);
            return
        }
        this.getSaveToDriveBubble_().showAt(this.$.toolbar.getSaveToDriveBubbleAnchor());
        recordShowSaveToDriveBubbleMetrics(this.saveToDriveState_)
    }
    onSaveToDriveBubbleAction_(e) {
        recordSaveToDriveBubbleActionMetrics(e.detail);
        switch (e.detail) {
        case SaveToDriveBubbleRequestType.CANCEL_UPLOAD:
            PdfViewerPrivateProxyImpl.getInstance().saveToDrive();
            this.saveToDriveState_ = SaveToDriveState.UNINITIALIZED;
            break;
        case SaveToDriveBubbleRequestType.MANAGE_STORAGE:
            assert(this.saveToDriveProgress_.accountEmail);
            this.handleNavigate_(getSaveToDriveManageStorageUrl(this.saveToDriveProgress_.accountEmail, this.saveToDriveProgress_.accountIsManaged ?? false), WindowOpenDisposition.NEW_FOREGROUND_TAB);
            this.saveToDriveState_ = SaveToDriveState.UNINITIALIZED;
            break;
        case SaveToDriveBubbleRequestType.OPEN_IN_DRIVE:
            assert(this.saveToDriveProgress_.accountEmail);
            assert(this.saveToDriveProgress_.driveItemId);
            this.handleNavigate_(getSaveToDriveOpenInDriveUrl(this.saveToDriveProgress_.accountEmail, this.saveToDriveProgress_.driveItemId), WindowOpenDisposition.NEW_FOREGROUND_TAB);
            this.saveToDriveState_ = SaveToDriveState.UNINITIALIZED;
            break;
        case SaveToDriveBubbleRequestType.RETRY:
            PdfViewerPrivateProxyImpl.getInstance().saveToDrive(this.saveToDriveRequestType_);
            recordSaveToDriveBubbleRetryMetrics(this.saveToDriveRequestType_, this.hasCommittedEdits_());
            break;
        case SaveToDriveBubbleRequestType.DIALOG_CLOSED:
            if (saveToDriveStateIsFinalState(this.saveToDriveState_)) {
                this.saveToDriveState_ = SaveToDriveState.UNINITIALIZED
            }
            break;
        default:
            console.warn("Saving to Drive bubble action is not implemented yet.", e.detail);
            break
        }
    }
    getSaveToDriveBubble_() {
        const bubble = this.shadowRoot.querySelector("viewer-save-to-drive-bubble");
        assert(bubble);
        return bubble
    }
    onSaveToDriveStateChanged_(oldState) {
        const newState = this.saveToDriveState_;
        if (saveToDriveStateIsFinalState(newState)) {
            if (newState === SaveToDriveState.SUCCESS) {
                this.onSaveSuccessful_(this.saveToDriveRequestType_)
            } else if (oldState === SaveToDriveState.UPLOADING) {
                this.onSaveFailedOrCancelled_(this.saveToDriveRequestType_)
            }
            this.getSaveToDriveBubble_().showAt(this.$.toolbar.getSaveToDriveBubbleAnchor(), true);
            return
        }
        if (newState === SaveToDriveState.UPLOADING) {
            this.setShowBeforeUnloadDialog_(true);
            if (isEditedSaveRequestType(this.saveToDriveRequestType_)) {
                this.hasUnsavedEdits_ = false
            }
            return
        }
        assert(newState === SaveToDriveState.UNINITIALIZED, `Unexpected state: ${newState}`);
        if (oldState !== SaveToDriveState.UPLOADING) {
            this.setShowBeforeUnloadDialog_(this.hasUnsavedEdits_)
        }
    }
    onRotateLeft_() {
        this.rotateCounterclockwise()
    }
    onChangePage_(e) {
        this.viewport.goToPage(e.detail.page);
        if (e.detail.origin === ChangePageOrigin.BOOKMARK) {
            record(UserAction.FOLLOW_BOOKMARK)
        } else if (e.detail.origin === ChangePageOrigin.PAGE_SELECTOR) {
            record(UserAction.PAGE_SELECTOR_NAVIGATE)
        } else if (e.detail.origin === ChangePageOrigin.THUMBNAIL) {
            record(UserAction.THUMBNAIL_NAVIGATE)
        }
    }
    onChangePageAndXy_(e) {
        const point = this.viewport.convertPageToScreen(e.detail.page, e.detail);
        this.goToPageAndXy_(e.detail.origin, e.detail.page, point)
    }
    onNavigate_(e) {
        const disposition = e.detail.newtab ? WindowOpenDisposition.NEW_BACKGROUND_TAB : WindowOpenDisposition.CURRENT_TAB;
        this.navigator_.navigate(e.detail.uri, disposition)
    }
    onSidenavToggleClick_() {
        this.sidenavCollapsed_ = !this.sidenavCollapsed_;
        const container = this.shadowRoot.querySelector("#sidenav-container");
        if (!this.sidenavCollapsed_) {
            container.classList.add("floating");
            container.addEventListener("transitionend", ( () => {
                container.classList.remove("floating")
            }
            ), {
                once: true
            })
        }
        LocalStorageProxyImpl.getInstance().setItem(LOCAL_STORAGE_SIDENAV_COLLAPSED_KEY, this.sidenavCollapsed_ ? "1" : "0")
    }
    handleUndoRedoStateChanged_(e) {
        this.hasCommittedInk2Edits_ = e.detail.canUndo;
        this.hasUnsavedEdits_ = e.detail.hasUnsavedEdits;
        this.setShowBeforeUnloadDialog_(this.shouldShowBeforeUnloadDialog_())
    }
    maybeRenderTextDirectiveHighlights_(url) {
        assert(this.paramsParser);
        const textDirectives = this.paramsParser.getTextFragments(url);
        if (textDirectives.length > 0) {
            this.pluginController_.highlightTextFragments(textDirectives)
        }
    }
    async selectFileAndGetWritable_(suggestedName) {
        assert(this.pdfUseShowSaveFilePicker_);
        const fileHandle = await window.showSaveFilePicker({
            suggestedName: suggestedName,
            types: [{
                description: "PDF Files",
                accept: {
                    "application/pdf": [".pdf"]
                }
            }]
        });
        return fileHandle.createWritable()
    }
    async selectFileAndGetWriter_(suggestedName) {
        assert(!this.pdfUseShowSaveFilePicker_);
        return new Promise((resolve => {
            chrome.fileSystem.chooseEntry({
                type: "saveFile",
                accepts: [{
                    description: "*.pdf",
                    extensions: ["pdf"]
                }],
                suggestedName: suggestedName
            }, (entry => {
                if (chrome.runtime.lastError) {
                    if (chrome.runtime.lastError.message !== "User cancelled") {
                        console.error("chrome.fileSystem.chooseEntry failed: " + chrome.runtime.lastError.message)
                    }
                    resolve(null)
                }
                assert(entry);
                entry.createWriter((writer => {
                    resolve(writer)
                }
                ))
            }
            ))
        }
        ))
    }
    writeToWriter_(writer, blob) {
        return new Promise(( (resolve, reject) => {
            writer.onwriteend = () => resolve();
            writer.onerror = () => reject(writer.error);
            writer.write(blob)
        }
        ))
    }
    async save_(requestType) {
        this.recordSaveMetrics_(requestType);
        assert(this.currentController);
        await this.maybeCommitActiveTextbox_();
        if (isEditedSaveRequestType(requestType)) {
            this.hasUnsavedEdits_ = false;
            if (this.pdfInk2Enabled_ && requestType === SaveRequestType.ANNOTATION) {
                Ink2Manager.getInstance().initiateSave()
            }
        }
        this.fire("save-initiated-for-testing");
        if (this.pdfGetSaveDataInBlocks_) {
            this.saveInBlocks_(requestType);
            return
        }
        const result = await this.currentController.save(requestType);
        if (result === null) {
            this.fire("save-completed-for-testing");
            return
        }
        let fileName = result.fileName;
        if (!fileName.toLowerCase().endsWith(".pdf")) {
            fileName = fileName + ".pdf"
        }
        if (result.bypassSaveFileForTesting) {
            this.onSaveSuccessful_(requestType);
            return
        }
        const blob = new Blob([result.dataToSave],{
            type: "application/pdf"
        });
        if (!this.pdfUseShowSaveFilePicker_) {
            const writer = await this.selectFileAndGetWriter_(fileName);
            if (writer === null) {
                this.onSaveFailedOrCancelled_(requestType);
                return
            }
            writer.write(blob);
            this.onSaveSuccessful_(requestType);
            return
        }
        try {
            const writable = await this.selectFileAndGetWritable_(fileName);
            await writable.write(blob);
            await writable.close();
            this.onSaveSuccessful_(requestType)
        } catch (error) {
            if (error instanceof Error && error.name !== "AbortError") {
                console.error("window.showSaveFilePicker failed: " + error)
            }
            this.onSaveFailedOrCancelled_(requestType)
        }
    }
    async saveInBlocks_(requestType) {
        assert(this.pluginController_.isActive);
        const nameResult = await this.pluginController_.getSuggestedFileName(requestType);
        let fileName = nameResult.fileName;
        if (!fileName.toLowerCase().endsWith(".pdf")) {
            fileName = fileName + ".pdf"
        }
        if (nameResult.bypassSaveFileForTesting) {
            this.onSaveSuccessful_(requestType);
            return
        }
        try {
            let writable;
            let writer;
            if (this.pdfUseShowSaveFilePicker_) {
                writable = await this.selectFileAndGetWritable_(fileName);
                writer = null
            } else {
                writer = await this.selectFileAndGetWriter_(fileName);
                if (writer === null) {
                    this.onSaveFailedOrCancelled_(requestType);
                    return
                }
                writable = null
            }
            let totalFileSize = 0;
            let offset = 0;
            do {
                const MAX_SAVE_BUFFER_SIZE = 16 * 1e3 * 1e3;
                const blockSize = Math.min(totalFileSize - offset, MAX_SAVE_BUFFER_SIZE);
                const result = await this.pluginController_.getSaveDataBlock(requestType, offset, blockSize);
                if (offset === 0) {
                    totalFileSize = result.totalFileSize;
                    if (totalFileSize === 0) {
                        throw new Error("File size is zero.")
                    }
                    verifyPdfHeader(result.dataToSave);
                    assert(result.dataToSave.byteLength !== 0)
                } else {
                    assert(result.dataToSave.byteLength === blockSize)
                }
                offset += result.dataToSave.byteLength;
                if (writable !== null) {
                    await writable.write(result.dataToSave)
                } else {
                    assert(writer !== null);
                    const blob = new Blob([result.dataToSave],{
                        type: "application/pdf"
                    });
                    await this.writeToWriter_(writer, blob)
                }
            } while (offset < totalFileSize);
            if (writable !== null) {
                await writable.close()
            }
            this.onSaveSuccessful_(requestType)
        } catch (error) {
            this.pluginController_.releaseSaveInBlockBuffers();
            if (error instanceof Error && error.name !== "AbortError") {
                console.error("window.showSaveFilePicker failed: " + error)
            }
            this.onSaveFailedOrCancelled_(requestType)
        }
    }
    onSaveSuccessful_(requestType) {
        this.setShowBeforeUnloadDialog_(this.shouldShowBeforeUnloadDialog_());
        if (this.pdfInk2Enabled_ && requestType === SaveRequestType.ANNOTATION) {
            Ink2Manager.getInstance().saved()
        }
        this.fire("save-completed-for-testing")
    }
    shouldShowBeforeUnloadDialog_() {
        let showBeforeUnloadDialog = this.hasUnsavedEdits_;
        showBeforeUnloadDialog = showBeforeUnloadDialog || this.isSaveToDriveUploading_();
        return showBeforeUnloadDialog
    }
    recordSaveMetrics_(requestType) {
        record(UserAction.SAVE);
        switch (requestType) {
        case SaveRequestType.ANNOTATION:
            record(UserAction.SAVE_WITH_INK2_ANNOTATION);
            break;
        case SaveRequestType.ORIGINAL:
            record(this.hasCommittedEdits_() ? UserAction.SAVE_ORIGINAL : UserAction.SAVE_ORIGINAL_ONLY);
            break;
        case SaveRequestType.EDITED:
            record(UserAction.SAVE_EDITED);
            break;
        case SaveRequestType.SEARCHIFIED:
            record(UserAction.SAVE_SEARCHIFIED);
            break;
        default:
            assertNotReachedCase()
        }
    }
    onGlicSummarize_() {
        PdfViewerPrivateProxyImpl.getInstance().glicSummarize()
    }
    async onPrint_() {
        record(UserAction.PRINT);
        assert(this.currentController);
        await this.maybeCommitActiveTextbox_();
        this.currentController.print()
    }
    annotationAvailable_() {
        return this.canSerializeDocument_ && !this.hadPassword_
    }
    isRotated_() {
        return this.clockwiseRotations_ !== 0
    }
    isTextboxActive_() {
        return this.textboxState_ !== TextBoxState.INACTIVE
    }
    maybeCommitActiveTextbox_() {
        if (!this.isTextboxActive_()) {
            return Promise.resolve()
        }
        const annotations = this.shadowRoot.querySelector("ink-text-annotations");
        assert(annotations);
        return annotations.commitActiveAnnotation()
    }
    isInTextAnnotationMode_() {
        return this.annotationMode_ === AnnotationMode.TEXT
    }
    shouldShowInkBottomToolbar_() {
        return this.inInk2AnnotationMode_() && !this.useSidePanelForInk_
    }
    shouldShowInkSidePanel_() {
        return this.inInk2AnnotationMode_() && this.useSidePanelForInk_
    }
    hasInk2AnnotationEdits_() {
        return this.textboxState_ === TextBoxState.EDITED || this.hasCommittedInk2Edits_
    }
    onSaveFailedOrCancelled_(requestType) {
        if (isEditedSaveRequestType(requestType)) {
            this.hasUnsavedEdits_ = true
        }
        if (this.pdfInk2Enabled_ && requestType === SaveRequestType.ANNOTATION) {
            Ink2Manager.getInstance().cancelSave()
        }
        this.setShowBeforeUnloadDialog_(this.shouldShowBeforeUnloadDialog_());
        this.fire("save-completed-for-testing")
    }
    onTextBoxStateChanged_(e) {
        this.textboxState_ = e.detail;
        if (e.detail === TextBoxState.INACTIVE) {
            this.focusPlugin_()
        } else if (e.detail === TextBoxState.EDITED) {
            this.setShowBeforeUnloadDialog_(true)
        }
    }
    inInk2AnnotationMode_() {
        return this.pdfInk2Enabled_ && this.annotationMode_ !== AnnotationMode.OFF
    }
    onBeforeUnload_(event) {
        if (this.pdfOopifEnabled && this.showBeforeUnloadDialog_) {
            BeforeUnloadProxyImpl.getInstance().preventDefault(event)
        }
    }
    setShowBeforeUnloadDialog_(showDialog) {
        if (this.showBeforeUnloadDialog_ === showDialog) {
            return
        }
        this.showBeforeUnloadDialog_ = showDialog;
        if (!this.pdfOopifEnabled) {
            chrome.mimeHandlerPrivate.setShowBeforeUnloadDialog(showDialog)
        }
    }
}
customElements.define(PdfViewerElement.is, PdfViewerElement);
export {AnnotationBrushType, AnnotationMode, BeforeUnloadProxyImpl, ChangePageOrigin, CrActionMenuElement, DEFAULT_TEXTBOX_WIDTH, FittingType, FormFieldFocusType, HIGHLIGHTER_COLORS, HIGHLIGHTER_SIZES, Ink2Manager, InkAnnotationBrushMixin, InkAnnotationTextMixin, InkBrushSelectorElement, InkColorSelectorElement, InkSizeSelectorElement, InkTextAnnotationsElement, InkTextBoxElement, LANDSCAPE_WIDTH, MIN_TEXTBOX_SIZE_PX, PAINTED_ATTRIBUTE, PEN_COLORS, PEN_SIZES, PORTRAIT_WIDTH, PdfNavigatorImpl, PdfViewerBaseElement, PdfViewerElement, PdfViewerPrivateProxyImpl, PluginController, PluginControllerEventType, PostMessageDataType, SaveToDriveBubbleAction, SaveToDriveBubbleRequestType, SaveToDriveBubbleState, SaveToDriveSaveType, SaveToDriveState, SelectableIconButtonElement, TEXT_COLORS, TEXT_SIZES, TextAlignment, TextAlignmentSelectorElement, TextAnnotationSource, TextBoxState, TextStyle, TextStylesSelectorElement, TextTypeface, UndoRedoStack, UserAction, ViewerAttachmentBarElement, ViewerAttachmentElement, ViewerBookmarkElement, ViewerBottomToolbarDropdownElement, ViewerBottomToolbarElement, ViewerDocumentOutlineElement, ViewerDownloadControlsElement, ViewerPageSelectorElement, ViewerPasswordDialogElement, ViewerPdfSidenavElement, ViewerPropertiesDialogElement, ViewerSaveControlsMixin, ViewerSaveToDriveBubbleElement, ViewerSaveToDriveControlsElement, ViewerSidePanelElement, ViewerTextBottomToolbarElement, ViewerTextSidePanelElement, ViewerThumbnailBarElement, ViewerThumbnailElement, ViewerToolbarElement, WindowOpenDisposition, colorsEqual, convertRotatedCoordinates, getFilenameFromURL, hexToColor, pageToScreenCoordinates, record, screenToPageCoordinates, shouldIgnoreKeyEvents};
