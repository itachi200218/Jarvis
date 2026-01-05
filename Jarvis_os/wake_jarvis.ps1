Add-Type -AssemblyName System.Speech

$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
$recognizer.SetInputToDefaultAudioDevice()

# ==============================
# WAKE WORD GRAMMAR (STRICT)
# ==============================
$wakeChoices = New-Object System.Speech.Recognition.Choices
$wakeChoices.Add("hey jarvis")
$wakeChoices.Add("hello jarvis")
$wakeChoices.Add("jarvis")

$wakeGrammar = New-Object System.Speech.Recognition.Grammar(
    New-Object System.Speech.Recognition.GrammarBuilder($wakeChoices)
)

$recognizer.LoadGrammar($wakeGrammar)

Write-Host "🟢 Jarvis is running (wake-word enabled)"
Write-Host "🎧 Listening for wake word..."

# ==============================
# WAKE HANDLER
# ==============================
Register-ObjectEvent -InputObject $recognizer -EventName SpeechRecognized -Action {

    $wakeText = $Event.SourceEventArgs.Result.Text.ToLower()
    Write-Host "🟢 Wake detected:" $wakeText

    # Stop wake listening
    $recognizer.RecognizeAsyncStop()

    # Greet if ONLY wake word
    python main.py --greet

    Start-Sleep -Milliseconds 500

    # ==============================
    # COMMAND LISTENER (FREE SPEECH)
    # ==============================
    $cmdRecognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    $cmdRecognizer.SetInputToDefaultAudioDevice()

    $dictation = New-Object System.Speech.Recognition.DictationGrammar
    $cmdRecognizer.LoadGrammar($dictation)

    Write-Host "🎙️ Listening for command..."

    $cmdRecognizer.Recognize()

    $commandText = $cmdRecognizer.Recognize().Text.ToLower()
    Write-Host "➡️ Command heard:" $commandText

    # Send FULL RAW command to Python brain
    python main.py --command "$commandText"

    # Restart wake listener
    $recognizer.RecognizeAsync([System.Speech.Recognition.RecognizeMode]::Multiple)
}

$recognizer.RecognizeAsync([System.Speech.Recognition.RecognizeMode]::Multiple)

# 🔥 KEEP SCRIPT ALIVE
while ($true) {
    Start-Sleep -Seconds 1
}
