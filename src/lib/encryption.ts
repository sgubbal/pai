import { KMSClient, EncryptCommand, DecryptCommand, GenerateDataKeyCommand } from '@aws-sdk/client-kms';
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

const kmsClient = new KMSClient({ region: process.env.AWS_REGION || 'us-east-1' });
const KMS_KEY_ID = process.env.KMS_KEY_ID!;

/**
 * Client-side encryption utilities using envelope encryption
 * 1. Generate data key using KMS
 * 2. Encrypt data with data key (AES-256-GCM)
 * 3. Store encrypted data + encrypted data key
 */

interface EncryptedData {
  encryptedDataKey: string;
  iv: string;
  authTag: string;
  ciphertext: string;
}

/**
 * Encrypt data using envelope encryption
 */
export async function encrypt(plaintext: string): Promise<EncryptedData> {
  // Generate data key from KMS
  const { Plaintext: dataKey, CiphertextBlob: encryptedDataKey } = await kmsClient.send(
    new GenerateDataKeyCommand({
      KeyId: KMS_KEY_ID,
      KeySpec: 'AES_256',
    })
  );

  if (!dataKey || !encryptedDataKey) {
    throw new Error('Failed to generate data key');
  }

  // Generate IV
  const iv = randomBytes(12);

  // Create cipher
  const cipher = createCipheriv('aes-256-gcm', Buffer.from(dataKey), iv);

  // Encrypt data
  let ciphertext = cipher.update(plaintext, 'utf8', 'base64');
  ciphertext += cipher.final('base64');

  // Get auth tag
  const authTag = cipher.getAuthTag();

  return {
    encryptedDataKey: Buffer.from(encryptedDataKey).toString('base64'),
    iv: iv.toString('base64'),
    authTag: authTag.toString('base64'),
    ciphertext,
  };
}

/**
 * Decrypt data using envelope encryption
 */
export async function decrypt(encryptedData: EncryptedData): Promise<string> {
  // Decrypt data key using KMS
  const { Plaintext: dataKey } = await kmsClient.send(
    new DecryptCommand({
      CiphertextBlob: Buffer.from(encryptedData.encryptedDataKey, 'base64'),
      KeyId: KMS_KEY_ID,
    })
  );

  if (!dataKey) {
    throw new Error('Failed to decrypt data key');
  }

  // Create decipher
  const decipher = createDecipheriv(
    'aes-256-gcm',
    Buffer.from(dataKey),
    Buffer.from(encryptedData.iv, 'base64')
  );

  // Set auth tag
  decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'base64'));

  // Decrypt data
  let plaintext = decipher.update(encryptedData.ciphertext, 'base64', 'utf8');
  plaintext += decipher.final('utf8');

  return plaintext;
}

/**
 * Encrypt object for storage
 */
export async function encryptObject<T>(obj: T): Promise<EncryptedData> {
  const plaintext = JSON.stringify(obj);
  return encrypt(plaintext);
}

/**
 * Decrypt object from storage
 */
export async function decryptObject<T>(encryptedData: EncryptedData): Promise<T> {
  const plaintext = await decrypt(encryptedData);
  return JSON.parse(plaintext) as T;
}
