"use strict";

/* =========================================================
   MIP - Meeting Intelligent Platform
   Main Frontend JavaScript
   ========================================================= */


/* =========================================================
   متغیرهای عمومی
   ========================================================= */

let mediaRecorder = null;
let audioChunks = [];
let recordedBlob = null;
let selectedAudioFile = null;

let recordTimerInterval = null;
let recordStartTime = null;

let currentMarkdownFile = null;


/*
 * Tagهای فعلی جلسه
 *
 * ساختار:
 *
 * [
 *   {
 *      tag: "MVP",
 *      category: "product",
 *      score: 2
 *   }
 * ]
 */
let meetingTags = [];


/* =========================================================
   ابزار انتخاب عنصر
   ========================================================= */

function $(selector) {
    return document.querySelector(selector);
}


/* =========================================================
   وضعیت عمومی
   ========================================================= */

function setGlobalStatus(
    message,
    success = true
) {

    const text = $("#globalStatusText");

    if (text) {
        text.textContent = message;
    }

    const status = $("#globalStatus");

    if (status) {

        status.classList.toggle(
            "success",
            success
        );

        status.classList.toggle(
            "error",
            !success
        );
    }
}


function showAudioUploadStatus(
    message,
    success = true
) {

    setGlobalStatus(
        message,
        success
    );
}


/* =========================================================
   ابزارهای عمومی
   ========================================================= */

function formatFileSize(bytes) {

    if (!bytes || bytes <= 0) {
        return "۰ بایت";
    }

    const units = [
        "بایت",
        "KB",
        "MB",
        "GB"
    ];

    let size = bytes;
    let index = 0;

    while (
        size >= 1024 &&
        index < units.length - 1
    ) {

        size /= 1024;
        index++;
    }

    return `${size.toFixed(
        index === 0 ? 0 : 1
    )} ${units[index]}`;
}


function toPersianNumber(value) {

    return String(value).replace(
        /\d/g,
        digit => "۰۱۲۳۴۵۶۷۸۹"[digit]
    );
}


function formatTextSize(text) {

    const blob = new Blob([
        text || ""
    ]);

    return formatFileSize(
        blob.size
    );
}


/* =========================================================
   فایل صوتی
   ========================================================= */

function handleAudioFile(file) {

    if (!file) {
        return;
    }

    selectedAudioFile = file;

    const name = $("#audioName");
    const size = $("#audioSize");
    const container = $("#audioSelected");

    if (name) {
        name.textContent = file.name;
    }

    if (size) {
        size.textContent =
            formatFileSize(file.size);
    }

    if (container) {
        container.classList.remove("hidden");
    }

    setGlobalStatus(
        `فایل صوتی «${file.name}» انتخاب شد.`,
        true
    );
}


function removeAudioFile() {

    selectedAudioFile = null;
    recordedBlob = null;

    const input = $("#audioFile");

    if (input) {
        input.value = "";
    }

    const container = $("#audioSelected");

    if (container) {
        container.classList.add("hidden");
    }

    const name = $("#audioName");
    const size = $("#audioSize");

    if (name) {
        name.textContent = "";
    }

    if (size) {
        size.textContent = "";
    }

    setGlobalStatus(
        "فایل صوتی حذف شد.",
        true
    );
}


/* =========================================================
   ضبط صدا
   ========================================================= */

async function startRecording() {

    if (
        !navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia
    ) {

        setGlobalStatus(
            "مرورگر شما از ضبط صدا پشتیبانی نمی‌کند.",
            false
        );

        return;
    }

    try {

        const stream =
            await navigator.mediaDevices.getUserMedia({
                audio: true
            });

        audioChunks = [];
        recordedBlob = null;

        let mimeType = "";


        if (
            MediaRecorder.isTypeSupported(
                "audio/webm;codecs=opus"
            )
        ) {

            mimeType =
                "audio/webm;codecs=opus";

        } else if (
            MediaRecorder.isTypeSupported(
                "audio/webm"
            )
        ) {

            mimeType =
                "audio/webm";
        }


        mediaRecorder =
            mimeType
                ? new MediaRecorder(
                    stream,
                    { mimeType }
                )
                : new MediaRecorder(stream);


        mediaRecorder.ondataavailable =
            function (event) {

                if (
                    event.data &&
                    event.data.size > 0
                ) {

                    audioChunks.push(
                        event.data
                    );
                }
            };


        mediaRecorder.onstop =
            function () {

                const type =
                    mediaRecorder.mimeType ||
                    "audio/webm";

                recordedBlob =
                    new Blob(
                        audioChunks,
                        { type }
                    );

                selectedAudioFile =
                    new File(
                        [recordedBlob],
                        "recording.webm",
                        { type }
                    );

                handleAudioFile(
                    selectedAudioFile
                );

                stream
                    .getTracks()
                    .forEach(
                        track =>
                            track.stop()
                    );
            };


        mediaRecorder.start();

        recordStartTime =
            Date.now();

        startRecordTimer();


        const startButton =
            $("#startRecord");

        const stopButton =
            $("#stopRecord");

        const state =
            $("#recordState");


        if (startButton) {
            startButton.disabled = true;
        }

        if (stopButton) {
            stopButton.disabled = false;
        }

        if (state) {

            state.textContent =
                "در حال ضبط";

            state.classList.remove(
                "record-ready"
            );

            state.classList.add(
                "recording"
            );
        }


        setGlobalStatus(
            "ضبط جلسه آغاز شد.",
            true
        );

    } catch (error) {

        console.error(
            "Recording error:",
            error
        );

        setGlobalStatus(
            "دسترسی به میکروفون برقرار نشد.",
            false
        );
    }
}


function stopRecording() {

    if (
        !mediaRecorder ||
        mediaRecorder.state === "inactive"
    ) {

        return;
    }

    mediaRecorder.stop();

    stopRecordTimer();


    const startButton =
        $("#startRecord");

    const stopButton =
        $("#stopRecord");

    const state =
        $("#recordState");


    if (startButton) {
        startButton.disabled = false;
    }

    if (stopButton) {
        stopButton.disabled = true;
    }

    if (state) {

        state.textContent =
            "ضبط متوقف شد";

        state.classList.remove(
            "recording"
        );

        state.classList.add(
            "record-ready"
        );
    }


    setGlobalStatus(
        "ضبط جلسه پایان یافت. فایل آماده پردازش است.",
        true
    );
}


function resetRecording() {

    if (
        mediaRecorder &&
        mediaRecorder.state !== "inactive"
    ) {

        mediaRecorder.stop();
    }

    mediaRecorder = null;

    audioChunks = [];

    recordedBlob = null;

    recordStartTime = null;

    stopRecordTimer();

    removeAudioFile();


    const timer =
        $("#recordTimer");

    const state =
        $("#recordState");


    if (timer) {
        timer.textContent =
            "00:00:00";
    }

    if (state) {
        state.textContent =
            "آماده ضبط";
    }


    const startButton =
        $("#startRecord");

    const stopButton =
        $("#stopRecord");


    if (startButton) {
        startButton.disabled = false;
    }

    if (stopButton) {
        stopButton.disabled = true;
    }


    setGlobalStatus(
        "ضبط صدا بازنشانی شد.",
        true
    );
}


/* =========================================================
   تایمر
   ========================================================= */

function startRecordTimer() {

    stopRecordTimer();

    recordTimerInterval =
        setInterval(
            function () {

                if (!recordStartTime) {
                    return;
                }

                const elapsed =
                    Math.floor(
                        (
                            Date.now() -
                            recordStartTime
                        ) / 1000
                    );

                const hours =
                    String(
                        Math.floor(
                            elapsed / 3600
                        )
                    ).padStart(2, "0");

                const minutes =
                    String(
                        Math.floor(
                            (elapsed % 3600) / 60
                        )
                    ).padStart(2, "0");

                const seconds =
                    String(
                        elapsed % 60
                    ).padStart(2, "0");

                const timer =
                    $("#recordTimer");

                if (timer) {

                    timer.textContent =
                        `${hours}:${minutes}:${seconds}`;
                }

            },
            1000
        );
}


function stopRecordTimer() {

    if (recordTimerInterval) {

        clearInterval(
            recordTimerInterval
        );

        recordTimerInterval = null;
    }
}


/* =========================================================
   تولید صورتجلسه
   ========================================================= */

async function generateMinutes() {

    let audioFile =
        selectedAudioFile;

    const fileInput =
        $("#audioFile");


    if (
        !audioFile &&
        fileInput &&
        fileInput.files &&
        fileInput.files.length > 0
    ) {

        audioFile =
            fileInput.files[0];

        selectedAudioFile =
            audioFile;
    }


    if (
        !audioFile &&
        recordedBlob
    ) {

        audioFile =
            new File(
                [recordedBlob],
                "recording.webm",
                {
                    type:
                        recordedBlob.type ||
                        "audio/webm"
                }
            );

        selectedAudioFile =
            audioFile;
    }


    if (!audioFile) {

        showAudioUploadStatus(
            "ابتدا فایل صوتی انتخاب یا ضبط کنید.",
            false
        );

        return;
    }


    const button =
        $("#generateButton");


    if (button) {

        button.disabled = true;

        button.textContent =
            "در حال تولید صورتجلسه...";
    }


    showAudioUploadStatus(
        "Whisper در حال پردازش فایل صوتی است...",
        true
    );


    const formData =
        new FormData();


    formData.append(
        "file",
        audioFile,
        audioFile.name
    );


    try {

        const response =
            await fetch(
                "/api/audio/transcribe",
                {
                    method: "POST",
                    body: formData
                }
            );


        let result;


        try {

            result =
                await response.json();

        } catch (error) {

            throw new Error(
                `پاسخ نامعتبر از سرور دریافت شد. HTTP ${response.status}`
            );
        }


        console.log(
            "API Result:",
            result
        );


        if (
            response.ok &&
            result.success
        ) {

            /*
             * نتیجه اصلی Backend
             */
            const meetingResult =
                result.result;


            /*
             * استخراج Tagهای Backend
             */
            extractMeetingTags(
                meetingResult
            );


            /*
             * نمایش نتیجه در Editor
             */
            const transcript =
                meetingResult ||
                result.transcript ||
                "";


            const displayText =
                typeof transcript === "string"
                    ? transcript
                    : JSON.stringify(
                        transcript,
                        null,
                        2
                    );


            showTranscript(
                displayText
            );


            setGlobalStatus(
                "صورتجلسه با موفقیت تولید شد.",
                true
            );


        } else {

            console.error(
                "API Error:",
                result
            );


            setGlobalStatus(
                result.detail ||
                result.message ||
                "تولید صورتجلسه ناموفق بود.",
                false
            );
        }


    } catch (error) {

        console.error(
            "Transcription error:",
            error
        );


        setGlobalStatus(
            error.message ||
            "ارتباط با سرور برقرار نشد.",
            false
        );


    } finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                "✨ تولید صورتجلسه";
        }
    }
}


/* =========================================================
   استخراج Tag از نتیجه Backend
   ========================================================= */

function extractMeetingTags(result) {

    meetingTags = [];


    if (!result) {

        renderTags();

        return;
    }


    if (
        typeof result === "object" &&
        Array.isArray(result.tags)
    ) {

        meetingTags =
            result.tags
                .filter(
                    item =>
                        item &&
                        item.tag
                )
                .map(
                    item => ({
                        tag: String(
                            item.tag
                        ).trim(),

                        category:
                            item.category || "",

                        score:
                            item.score || 0
                    })
                );
    }


    renderTags();
}


/* =========================================================
   نمایش Tagها
   ========================================================= */

function renderTags() {

    const suggestedContainer =
        $("#suggestedTags");

    const selectedContainer =
        $("#selectedTags");

    const hiddenInput =
        $("#meetingTags");


    if (!suggestedContainer) {
        return;
    }


    suggestedContainer.innerHTML = "";


    /*
     * اگر Tag نداریم
     */
    if (!meetingTags.length) {

        const empty =
            document.createElement("span");

        empty.textContent =
            "هنوز Tag پیشنهادی وجود ندارد.";

        empty.className =
            "tag-empty";

        suggestedContainer.appendChild(
            empty
        );

    } else {

        meetingTags.forEach(
            (item, index) => {

                const tag =
                    document.createElement("span");

                tag.className =
                    "tag-item";

                tag.textContent =
                    item.tag;


                const remove =
                    document.createElement("button");

                remove.type =
                    "button";

                remove.textContent =
                    "×";

                remove.title =
                    "حذف Tag";


                remove.addEventListener(
                    "click",
                    function () {

                        removeTag(index);
                    }
                );


                tag.appendChild(
                    remove
                );


                suggestedContainer.appendChild(
                    tag
                );
            }
        );
    }


    /*
     * برای سازگاری با Backend آینده،
     * مقدار نهایی Tagها در input مخفی قرار می‌گیرد.
     */
    if (hiddenInput) {

        hiddenInput.value =
            meetingTags
                .map(
                    item => item.tag
                )
                .join(",");
    }


    if (selectedContainer) {
        selectedContainer.innerHTML = "";
    }
}


/* =========================================================
   حذف Tag
   ========================================================= */

function removeTag(index) {

    if (
        index < 0 ||
        index >= meetingTags.length
    ) {

        return;
    }


    const removed =
        meetingTags[index];


    meetingTags.splice(
        index,
        1
    );


    renderTags();


    setGlobalStatus(
        `برچسب «${removed.tag}» حذف شد.`,
        true
    );
}


/* =========================================================
   افزودن Tag دستی
   ========================================================= */

function addManualTag() {

    const input =
        $("#meetingTagInput");


    if (!input) {
        return;
    }


    const value =
        input.value.trim();


    if (!value) {

        return;
    }


    /*
     * جلوگیری از Tag تکراری
     */
    const exists =
        meetingTags.some(
            item =>
                item.tag.toLowerCase() ===
                value.toLowerCase()
        );


    if (exists) {

        setGlobalStatus(
            "این Tag قبلاً اضافه شده است.",
            false
        );

        input.focus();

        return;
    }


    meetingTags.push({

        tag: value,

        category: "custom",

        score: 0

    });


    input.value = "";


    renderTags();


    setGlobalStatus(
        `برچسب «${value}» اضافه شد.`,
        true
    );


    input.focus();
}


/* =========================================================
   نمایش صورتجلسه
   ========================================================= */

function showTranscript(text) {

    const editor =
        $("#markdownEditor");


    if (!editor) {

        console.error(
            "markdownEditor not found."
        );

        return;
    }


    editor.value =
        text || "";


    currentMarkdownFile = null;


    const name =
        $("#mdName");

    const size =
        $("#mdSize");


    if (name) {

        name.textContent =
            "صورتجلسه تولیدشده.md";
    }


    if (size) {

        size.textContent =
            formatTextSize(
                editor.value
            );
    }


    const status =
        $("#editorStatus");


    if (status) {

        status.textContent =
            "صورتجلسه تولید شد و آماده ویرایش است.";
    }


    updateEditorStats();


    setGlobalStatus(
        "صورتجلسه آماده ویرایش است.",
        true
    );
}


/* =========================================================
   فایل Markdown
   ========================================================= */

function handleMarkdownFile(file) {

    if (!file) {
        return;
    }


    const filename =
        file.name.toLowerCase();


    if (
        !filename.endsWith(".md") &&
        file.type !== "text/markdown" &&
        file.type !== "text/plain"
    ) {

        setGlobalStatus(
            "لطفاً یک فایل با پسوند .md انتخاب کنید.",
            false
        );

        return;
    }


    const reader =
        new FileReader();


    reader.onload =
        function (event) {

            const text =
                event.target.result || "";


            currentMarkdownFile =
                file;


            const editor =
                $("#markdownEditor");


            if (editor) {

                editor.value =
                    text;
            }


            const name =
                $("#mdName");

            const size =
                $("#mdSize");


            if (name) {

                name.textContent =
                    file.name;
            }


            if (size) {

                size.textContent =
                    formatFileSize(
                        file.size
                    );
            }


            const status =
                $("#editorStatus");


            if (status) {

                status.textContent =
                    "فایل Markdown بارگذاری شد و آماده ویرایش است.";
            }


            updateEditorStats();


            setGlobalStatus(
                `فایل «${file.name}» نمایش داده شد.`,
                true
            );
        };


    reader.onerror =
        function () {

            setGlobalStatus(
                "خواندن فایل Markdown ناموفق بود.",
                false
            );
        };


    reader.readAsText(
        file,
        "UTF-8"
    );
}


/* =========================================================
   Editor Stats
   ========================================================= */

function updateEditorStats() {

    const editor =
        $("#markdownEditor");


    if (!editor) {
        return;
    }


    const text =
        editor.value || "";


    const words =
        text.trim()
            ? text.trim().split(/\s+/).length
            : 0;


    const chars =
        text.length;


    const wordCount =
        $("#wordCount");


    if (wordCount) {

        wordCount.textContent =
            `${toPersianNumber(words)} کلمه`;
    }


    const summaryWords =
        $("#summaryWords");


    if (summaryWords) {

        summaryWords.textContent =
            toPersianNumber(words);
    }


    const summaryChars =
        $("#summaryChars");


    if (summaryChars) {

        summaryChars.textContent =
            toPersianNumber(chars);
    }


    const saveChangesButton =
        $("#saveChangesButton");


    if (saveChangesButton) {

        saveChangesButton.disabled =
            !(
                editor.value &&
                editor.value.trim()
            );
    }


    updateStorageButton();
}


/* =========================================================
   ذخیره فایل Markdown
   ========================================================= */

function saveMarkdownFile() {

    const editor =
        $("#markdownEditor");


    if (
        !editor ||
        !editor.value.trim()
    ) {

        setGlobalStatus(
            "متنی برای ذخیره وجود ندارد.",
            false
        );

        return;
    }


    let filename =
        "meeting_report.md";


    if (currentMarkdownFile) {

        filename =
            currentMarkdownFile.name;
    }


    if (
        !filename
            .toLowerCase()
            .endsWith(".md")
    ) {

        filename += ".md";
    }


    const blob =
        new Blob(
            [editor.value],
            {
                type:
                    "text/markdown;charset=utf-8"
            }
        );


    const url =
        URL.createObjectURL(blob);


    const link =
        document.createElement("a");


    link.href =
        url;

    link.download =
        filename;


    document.body.appendChild(
        link
    );


    link.click();


    link.remove();


    URL.revokeObjectURL(
        url
    );


    const status =
        $("#editorStatus");


    if (status) {

        status.textContent =
            "فایل Markdown ذخیره شد.";
    }


    setGlobalStatus(
        "فایل Markdown با موفقیت ذخیره شد.",
        true
    );
}


/* =========================================================
   ذخیره واقعی تغییرات
   ========================================================= */

async function saveMarkdownChanges() {

    const editor =
        $("#markdownEditor");


    if (
        !editor ||
        !editor.value.trim()
    ) {

        setGlobalStatus(
            "متن صورتجلسه خالی است.",
            false
        );

        return;
    }


    const button =
        $("#saveChangesButton");


    if (button) {

        button.disabled = true;

        button.textContent =
            "در حال ذخیره...";
    }


    const status =
        $("#editorStatus");


    if (status) {

        status.textContent =
            "در حال ذخیره تغییرات...";
    }


    try {

        const response =
            await fetch(
                "/api/meeting/save",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        content:
                            editor.value
                    })
                }
            );


        const result =
            await response.json();


        if (
            response.ok &&
            result.success
        ) {

            if (status) {

                status.textContent =
                    "تغییرات صورتجلسه ذخیره شد.";
            }


            setGlobalStatus(
                "تغییرات صورتجلسه با موفقیت ذخیره شد.",
                true
            );

        } else {

            throw new Error(
                result.detail ||
                result.message ||
                "ذخیره صورتجلسه ناموفق بود."
            );
        }


    } catch (error) {

        console.error(
            "Save meeting error:",
            error
        );


        if (status) {

            status.textContent =
                "خطا در ذخیره تغییرات.";
        }


        setGlobalStatus(
            error.message ||
            "خطا در ذخیره صورتجلسه.",
            false
        );


    } finally {

        if (button) {

            button.disabled = false;

            button.textContent =
                "💾 ذخیره تغییرات";
        }
    }
}


/* =========================================================
   ChromaDB
   ========================================================= */

function updateStorageButton() {

    const editor =
        $("#markdownEditor");

    const button =
        $("#chromaButton");


    if (!button) {
        return;
    }


    const hasText =
        !!(
            editor &&
            editor.value &&
            editor.value.trim()
        );


    button.disabled =
        !hasText;
}


async function saveToChromaDB() {

    const editor =
        $("#markdownEditor");


    if (
        !editor ||
        !editor.value.trim()
    ) {

        setGlobalStatus(
            "ابتدا صورتجلسه را تولید یا فایل Markdown را انتخاب کنید.",
            false
        );

        return;
    }


    const title =
        $("#meetingTitle")?.value.trim() || "";


    const date =
        $("#meetingDate")?.value || "";


    const tags =
        meetingTags.map(
            item => item.tag
        );


    const button =
        $("#chromaButton");


    if (button) {

        button.disabled = true;

        button.textContent =
            "در حال ذخیره...";
    }


    const status =
        $("#storageStatus");


    if (status) {

        status.textContent =
            "در حال آماده‌سازی";
    }


    const payload = {

        content:
            editor.value,

        title:
            title,

        date:
            date,

        tags:
            tags
    };


    console.log(
        "ChromaDB payload:",
        payload
    );


    /*
     * Endpoint واقعی ChromaDB هنوز متصل نشده است.
     */

    await new Promise(
        resolve =>
            setTimeout(
                resolve,
                300
            )
    );


    if (status) {

        status.textContent =
            "آماده";
    }


    setGlobalStatus(
        "متن نهایی همراه با Tagها آماده ذخیره در ChromaDB است.",
        true
    );


    if (button) {

        button.disabled = false;

        button.textContent =
            "🗄️ ذخیره در ChromaDB";
    }
}


/* =========================================================
   Navigation
   ========================================================= */

function setupNavigation() {

    const items =
        document.querySelectorAll(
            ".nav-item"
        );


    items.forEach(
        item => {

            item.addEventListener(
                "click",
                function () {

                    items.forEach(
                        element =>
                            element.classList.remove(
                                "active"
                            )
                    );


                    item.classList.add(
                        "active"
                    );
                }
            );
        }
    );
}


/* =========================================================
   Markdown Toolbar
   ========================================================= */

function insertMarkdown(
    prefix,
    suffix = ""
) {

    const editor =
        $("#markdownEditor");


    if (!editor) {
        return;
    }


    const start =
        editor.selectionStart;


    const end =
        editor.selectionEnd;


    const selected =
        editor.value.substring(
            start,
            end
        );


    editor.setRangeText(
        prefix +
        selected +
        suffix,
        start,
        end,
        "select"
    );


    editor.focus();


    updateEditorStats();
}


function setupEditorToolbar() {

    const buttons =
        document.querySelectorAll(
            ".editor-tools button"
        );


    if (!buttons.length) {
        return;
    }


    if (buttons[0]) {

        buttons[0].addEventListener(
            "click",
            function () {

                document.execCommand(
                    "undo"
                );

                updateEditorStats();
            }
        );
    }


    if (buttons[1]) {

        buttons[1].addEventListener(
            "click",
            function () {

                document.execCommand(
                    "redo"
                );

                updateEditorStats();
            }
        );
    }


    if (buttons[2]) {

        buttons[2].addEventListener(
            "click",
            function () {

                insertMarkdown(
                    "# "
                );
            }
        );
    }


    if (buttons[3]) {

        buttons[3].addEventListener(
            "click",
            function () {

                insertMarkdown(
                    "## "
                );
            }
        );
    }


    if (buttons[4]) {

        buttons[4].addEventListener(
            "click",
            function () {

                insertMarkdown(
                    "**",
                    "**"
                );
            }
        );
    }


    if (buttons[5]) {

        buttons[5].addEventListener(
            "click",
            function () {

                insertMarkdown(
                    "*",
                    "*"
                );
            }
        );
    }


    if (buttons[6]) {

        buttons[6].addEventListener(
            "click",
            function () {

                insertMarkdown(
                    "- "
                );
            }
        );
    }


    if (buttons[7]) {

        buttons[7].addEventListener(
            "click",
            function () {

                insertMarkdown(
                    "1. "
                );
            }
        );
    }
}


/* =========================================================
   مقداردهی اولیه
   ========================================================= */

function initializeMIP() {

    console.log(
        "MIP frontend initializing..."
    );


    /* -----------------------------------------------------
       Audio File
       ----------------------------------------------------- */

    const audioFile =
        $("#audioFile");


    if (audioFile) {

        audioFile.addEventListener(
            "change",
            function () {

                if (
                    this.files &&
                    this.files.length > 0
                ) {

                    handleAudioFile(
                        this.files[0]
                    );
                }
            }
        );
    }


    /* -----------------------------------------------------
       Remove Audio
       ----------------------------------------------------- */

    const removeAudio =
        $("#removeAudio");


    if (removeAudio) {

        removeAudio.addEventListener(
            "click",
            removeAudioFile
        );
    }


    /* -----------------------------------------------------
       Recording
       ----------------------------------------------------- */

    const startRecord =
        $("#startRecord");

    const stopRecord =
        $("#stopRecord");

    const resetRecord =
        $("#resetRecord");


    if (startRecord) {

        startRecord.addEventListener(
            "click",
            startRecording
        );
    }


    if (stopRecord) {

        stopRecord.addEventListener(
            "click",
            stopRecording
        );
    }


    if (resetRecord) {

        resetRecord.addEventListener(
            "click",
            resetRecording
        );
    }


    /* -----------------------------------------------------
       Generate
       ----------------------------------------------------- */

    const generateButton =
        $("#generateButton");


    if (generateButton) {

        generateButton.addEventListener(
            "click",
            generateMinutes
        );

    } else {

        console.error(
            "Generate button NOT FOUND!"
        );
    }


    /* -----------------------------------------------------
       Markdown File
       ----------------------------------------------------- */

    const markdownFile =
        $("#markdownFile");


    if (markdownFile) {

        markdownFile.addEventListener(
            "change",
            function () {

                if (
                    this.files &&
                    this.files.length > 0
                ) {

                    handleMarkdownFile(
                        this.files[0]
                    );
                }
            }
        );
    }


    /* -----------------------------------------------------
       Editor
       ----------------------------------------------------- */

    const editor =
        $("#markdownEditor");


    if (editor) {

        editor.addEventListener(
            "input",
            updateEditorStats
        );
    }


    /* -----------------------------------------------------
       Save Markdown File
       ----------------------------------------------------- */

    const saveMdButton =
        $("#saveMdButton");


    if (saveMdButton) {

        saveMdButton.addEventListener(
            "click",
            saveMarkdownFile
        );
    }


    /* -----------------------------------------------------
       Save Changes
       ----------------------------------------------------- */

    const saveChangesButton =
        $("#saveChangesButton");


    if (saveChangesButton) {

        saveChangesButton.addEventListener(
            "click",
            saveMarkdownChanges
        );
    }


    /* -----------------------------------------------------
       ChromaDB
       ----------------------------------------------------- */

    const chromaButton =
        $("#chromaButton");


    if (chromaButton) {

        chromaButton.addEventListener(
            "click",
            saveToChromaDB
        );
    }


    /* -----------------------------------------------------
       Add Tag
       ----------------------------------------------------- */

    const addTagButton =
        $("#addTagButton");


    if (addTagButton) {

        addTagButton.addEventListener(
            "click",
            addManualTag
        );
    }


    const tagInput =
        $("#meetingTagInput");


    if (tagInput) {

        tagInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    addManualTag();
                }
            }
        );
    }


    /* -----------------------------------------------------
       Navigation
       ----------------------------------------------------- */

    setupNavigation();


    /* -----------------------------------------------------
       Toolbar
       ----------------------------------------------------- */

    setupEditorToolbar();


    /* -----------------------------------------------------
       وضعیت اولیه
       ----------------------------------------------------- */

    updateEditorStats();

    updateStorageButton();

    renderTags();


    setGlobalStatus(
        "آماده دریافت جلسه",
        true
    );


    console.log(
        "MIP frontend initialized successfully."
    );
}


/* =========================================================
   اجرای برنامه
   ========================================================= */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeMIP
    );

} else {

    initializeMIP();
}