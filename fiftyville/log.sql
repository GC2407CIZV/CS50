-- Keep a log of any SQL queries you execute as you solve the mystery.

-- 1. Find crime scene report about the theft
SELECT description, street
FROM crime_scene_reports
WHERE month = 7 AND day = 28

-- 2. Find interviews of the 3 witnesses

SELECT transcript, name
FROM interviews
WHERE month = 7 AND day = 28 AND transcript LIKE '%bakery%'

-- 3. Security footage from the bakery Car who left the pariking around the time of the crime

SELECT bakery_security_logs.hour, bakery_security_logs.minute, bakery_security_logs.activity, bakery_security_logs.license_plate, people.name
FROM people
JOIN bakery_security_logs ON bakery_security_logs.license_plate = people.license_plate
WHERE bakery_security_logs.month = 7
AND bakery_security_logs.day = 28
AND bakery_security_logs.hour = 10
AND bakery_security_logs.minute >= 10
AND bakery_security_logs.minute <= 30

-- 4. Search/ Narrow name a of culprit by transaction type
SELECT people.name, atm_transactions.transaction_type, atm_transactions.atm_location
FROM people
JOIN bank_accounts ON bank_accounts.person_id = people.id
JOIN atm_transactions ON atm_transactions.account_number = bank_accounts.account_number
WHERE atm_transactions.month = 7
AND atm_transactions.day = 28
AND atm_transactions.atm_location LIKE 'Leggett%'
AND atm_transactions.transaction_type = 'withdraw'

-- 5. Find caller and add his name
SELECT phone_calls.caller, people.name, phone_calls.receiver, phone_calls.duration
FROM phone_calls
JOIN people ON people.phone_number = phone_calls.caller
WHERE month = 7
AND day = 28
AND duration < 60

-- 6. Find airport destination id
SELECT   airports.city, flights.origin_airport_id,  flights.destination_airport_id, flights.hour, flights.minute
FROM flights
JOIN airports ON flights.origin_airport_id = airports.id
WHERE airports.city LIKE 'Fiftyville'
AND month = 7
AND day = 29
ORDER BY flights.hour

-- 7. Find destination
SELECT   airports.city,airports.full_name, flights.destination_airport_id, flights.hour
FROM flights
JOIN airports ON flights.destination_airport_id = airports.id
WHERE flights.destination_airport_id = 4
AND month = 7
AND day = 29
ORDER BY flights.hour

-- 8. Find accomplice
SELECT phone_calls.caller, phone_calls.receiver, people.name, phone_calls.duration
FROM phone_calls
JOIN people ON people.phone_number = phone_calls.receiver
WHERE month = 7
AND day = 28
AND phone_calls.caller LIKE '%367%'
AND duration < 60
