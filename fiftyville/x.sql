SELECT DISTINCT(people.passport_number), people.name, flights.hour
FROM atm_transactions
JOIN bank_accounts ON atm_transactions.account_number = bank_accounts.account_number
JOIN people ON bank_accounts.person_id = people.id
JOIN bakery_security_logs on people.license_plate = bakery_security_logs.license_plate
JOIN phone_calls ON people.phone_number = phone_calls.caller
JOIN passengers ON passengers.passport_number = people.passport_number
JOIN flights ON flights.id = passengers.flight_id

WHERE atm_transactions.atm_location LIKE 'Leggett%'
AND atm_transactions.month = 7
AND atm_transactions.day = 28
AND atm_transactions.transaction_type = 'withdraw'
AND bakery_security_logs.hour = 10
AND bakery_security_logs.minute >= 10
AND bakery_security_logs.minute <= 30
AND phone_calls.duration < 60
AND flights.day = 29
AND flights.month = 7

