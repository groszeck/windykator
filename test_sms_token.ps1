# Test tokenu SMSAPI w PowerShell
param(
    [string]$Token = "f9WVDUqFSUH6JOW40UyJubjCkGEJQxCGvce3Qs8A"
)

Write-Host "🧪 Test tokenu SMSAPI: $($Token.Substring(0,10))..." -ForegroundColor Yellow
Write-Host "=" * 70

# Test 1: OAuth Bearer Token - GET /profile
Write-Host "`n🧪 Test 1: OAuth Bearer Token - GET /profile" -ForegroundColor Cyan
Write-Host "📡 URL: https://api.smsapi.com/profile"

$headers = @{
    'Authorization' = "Bearer $Token"
    'Content-Type' = 'application/json'
}

try {
    $response = Invoke-RestMethod -Uri "https://api.smsapi.com/profile" -Method GET -Headers $headers -TimeoutSec 30
    Write-Host "✅ OAuth Bearer Token działa!" -ForegroundColor Green
    Write-Host "👤 Użytkownik: $($response.username)" -ForegroundColor Green
    Write-Host "💰 Punkty: $($response.points)" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "❌ OAuth Bearer Token nie działa: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: OAuth Bearer Token - fallback na api2.smsapi.com
Write-Host "`n🧪 Test 2: OAuth Bearer Token - api2.smsapi.com" -ForegroundColor Cyan
Write-Host "📡 URL: https://api2.smsapi.com/profile"

try {
    $response = Invoke-RestMethod -Uri "https://api2.smsapi.com/profile" -Method GET -Headers $headers -TimeoutSec 30
    Write-Host "✅ OAuth Bearer Token działa na api2!" -ForegroundColor Green
    Write-Host "👤 Użytkownik: $($response.username)" -ForegroundColor Green
    Write-Host "💰 Punkty: $($response.points)" -ForegroundColor Green
    exit 0
} catch {
    Write-Host "❌ OAuth Bearer Token nie działa na api2: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Standardowa autoryzacja - POST /profile
Write-Host "`n🧪 Test 3: Standardowa autoryzacja - POST /profile" -ForegroundColor Cyan
Write-Host "📡 URL: https://api.smsapi.com/profile"

$body = @{
    token = $Token
    format = 'json'
}

try {
    $response = Invoke-RestMethod -Uri "https://api.smsapi.com/profile" -Method POST -Body $body -TimeoutSec 30
    Write-Host "📄 Odpowiedź: $($response | ConvertTo-Json)" -ForegroundColor Gray
    
    if ($response.error -eq 0) {
        Write-Host "✅ Standardowa autoryzacja działa!" -ForegroundColor Green
        Write-Host "👤 Użytkownik: $($response.username)" -ForegroundColor Green
        Write-Host "💰 Punkty: $($response.points)" -ForegroundColor Green
        exit 0
    }
    Write-Host "❌ Standardowa autoryzacja nie działa: $($response.message)" -ForegroundColor Red
} catch {
    Write-Host "❌ Standardowa autoryzacja nie działa: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Wysyłanie SMS - form-data
Write-Host "`n🧪 Test 4: Wysyłanie SMS - form-data" -ForegroundColor Cyan
Write-Host "📡 URL: https://api.smsapi.com/sms.do"

$smsBody = @{
    token = $Token
    to = "test"
    message = "Test SMS API - $(Get-Date -Format 'HH:mm:ss')"
    format = 'json'
}

try {
    $response = Invoke-RestMethod -Uri "https://api.smsapi.com/sms.do" -Method POST -Body $smsBody -TimeoutSec 30
    Write-Host "📄 Odpowiedź SMS: $($response | ConvertTo-Json)" -ForegroundColor Gray
    
    if ($response.error -eq 0) {
        Write-Host "✅ Wysyłanie SMS działa!" -ForegroundColor Green
        Write-Host "📱 SMS ID: $($response.list[0].id)" -ForegroundColor Green
        exit 0
    }
    Write-Host "❌ Wysyłanie SMS nie działa: $($response.message)" -ForegroundColor Red
} catch {
    Write-Host "❌ Wysyłanie SMS nie działa: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + "=" * 70
Write-Host "❌ Wszystkie testy nie powiodły się!" -ForegroundColor Red
Write-Host "💡 Sprawdź w panelu SMSAPI czy token jest aktywny" -ForegroundColor Yellow
exit 1 