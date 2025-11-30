/**
 * Twilio SMS Alert Service
 * 
 * This module provides functionality to send SMS alerts to workers
 * regarding PPE compliance status using Twilio's messaging API.
 * 
 * To use in production:
 * 1. Sign up for a Twilio account at https://www.twilio.com
 * 2. Get your Account SID and Auth Token from the Twilio Console
 * 3. Purchase a Twilio phone number
 * 4. Add these to your environment variables:
 *    - TWILIO_ACCOUNT_SID
 *    - TWILIO_AUTH_TOKEN
 *    - TWILIO_PHONE_NUMBER
 * 5. Install the Twilio SDK: pnpm add twilio
 * 6. Uncomment the implementation code below
 */

// Uncomment this import when ready to use Twilio
// import twilio from 'twilio';

interface SendAlertParams {
  to: string;
  message: string;
  workerId: string;
  workerName: string;
}

interface AlertResponse {
  success: boolean;
  messageId?: string;
  error?: string;
}

/**
 * Send an SMS alert to a worker
 * 
 * @param params - Alert parameters including recipient phone number and message
 * @returns Promise with the result of the SMS send operation
 */
export async function sendSMSAlert(
  params: SendAlertParams
): Promise<AlertResponse> {
  try {
    // PRODUCTION IMPLEMENTATION (uncomment when ready):
    /*
    const accountSid = process.env.TWILIO_ACCOUNT_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;
    const fromNumber = process.env.TWILIO_PHONE_NUMBER;

    if (!accountSid || !authToken || !fromNumber) {
      throw new Error('Twilio credentials not configured');
    }

    const client = twilio(accountSid, authToken);

    const message = await client.messages.create({
      body: params.message,
      from: fromNumber,
      to: params.to,
    });

    console.log(`SMS sent to ${params.workerName} (${params.workerId}): ${message.sid}`);

    return {
      success: true,
      messageId: message.sid,
    };
    */

    // DEVELOPMENT MOCK IMPLEMENTATION:
    // eslint-disable-next-line no-console
    console.log('===== MOCK TWILIO SMS ALERT =====');
    // eslint-disable-next-line no-console
    console.log(`To: ${params.to}`);
    // eslint-disable-next-line no-console
    console.log(`Worker: ${params.workerName} (${params.workerId})`);
    // eslint-disable-next-line no-console
    console.log(`Message: ${params.message}`);
    // eslint-disable-next-line no-console
    console.log('================================');

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    return {
      success: true,
      messageId: `MOCK_${Date.now()}`,
    };
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Failed to send SMS alert:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Send bulk SMS alerts to multiple workers
 * 
 * @param alerts - Array of alert parameters for multiple workers
 * @returns Promise with results for all SMS send operations
 */
export async function sendBulkSMSAlerts(
  alerts: SendAlertParams[]
): Promise<AlertResponse[]> {
  const results = await Promise.all(
    alerts.map((alert) => sendSMSAlert(alert))
  );
  return results;
}

/**
 * Validate phone number format
 * 
 * @param phoneNumber - Phone number to validate
 * @returns true if the phone number is in valid E.164 format
 */
export function validatePhoneNumber(phoneNumber: string): boolean {
  // E.164 format: +[country code][number]
  const e164Regex = /^\+[1-9]\d{1,14}$/;
  return e164Regex.test(phoneNumber);
}

/**
 * Format phone number to E.164 format
 * 
 * @param phoneNumber - Phone number to format
 * @param defaultCountryCode - Default country code if not provided (default: '1' for US)
 * @returns Formatted phone number in E.164 format
 */
export function formatPhoneNumber(
  phoneNumber: string,
  defaultCountryCode: string = '1'
): string {
  // Remove all non-digit characters
  const cleaned = phoneNumber.replace(/\D/g, '');

  // Add country code if not present
  if (!cleaned.startsWith(defaultCountryCode)) {
    return `+${defaultCountryCode}${cleaned}`;
  }

  return `+${cleaned}`;
}
