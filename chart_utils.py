Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Users\yilmab> $compute = Invoke-RestMethod -Uri 'https://madam-dudu-astro-core-1.onrender.com/compute' `
>>   -Method POST `
>>   -Headers @{
>>     "Authorization" = "Bearer d0a7596a10c4315f7ecb6782a8243b98";
>>     "Content-Type" = "application/json"
>>   } `
>>   -Body '{
>>     "name": "Burak",
>>     "dob": "1995-11-08",
>>     "tob": "22:15",
>>     "city": "Ankara",
>>     "country": "Turkey"
>>   }'
PS C:\Users\yilmab> $chart = Invoke-RestMethod -Uri 'https://madam-dudu-astro-core-1.onrender.com/render' `
>>   -Method POST `
>>   -Headers @{
>>     "Authorization" = "Bearer d0a7596a10c4315f7ecb6782a8243b98";
>>     "Content-Type" = "application/json"
>>   } `
>>   -Body (@{
>>     name = $compute.input.name
>>     dob = $compute.input.dob
>>     tob = $compute.input.tob
>>     city = $compute.input.city
>>     country = $compute.input.country
>>     planets = @(
>>       @{ name = "Sun"; ecliptic_long = 221.5 },
>>       @{ name = "Moon"; ecliptic_long = 45.2 },
>>       @{ name = "Mercury"; ecliptic_long = 210.3 },
>>       @{ name = "Venus"; ecliptic_long = 200.1 },
>>       @{ name = "Mars"; ecliptic_long = 123.4 },
>>       @{ name = "Jupiter"; ecliptic_long = 305.7 },
>>       @{ name = "Saturn"; ecliptic_long = 275.8 },
>>       @{ name = "Uranus"; ecliptic_long = 180.9 },
>>       @{ name = "Neptune"; ecliptic_long = 330.6 },
>>       @{ name = "Pluto"; ecliptic_long = 240.4 }
>>     )
>>   } | ConvertTo-Json -Depth 10)
Invoke-RestMethod : The remote server returned an error: (500) Internal Server Error.
At line:1 char:10
+ $chart = Invoke-RestMethod -Uri 'https://madam-dudu-astro-core-1.onre ...
+          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand
