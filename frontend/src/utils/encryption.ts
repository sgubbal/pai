/**
 * Client-side encryption utilities using Web Crypto API
 * Note: This provides client-side encryption for data in transit.
 * The backend uses AWS KMS for server-side encryption.
 */

import { EncryptedData } from '../types';

const ALGORITHM = 'AES-GCM';
const KEY_LENGTH = 256;
const IV_LENGTH = 12; // 96 bits for GCM
const TAG_LENGTH = 128; // 128 bits for GCM auth tag

class EncryptionManager {
  private encryptionKey: CryptoKey | null = null;

  /**
   * Initialize encryption by generating or retrieving encryption key
   */
  async initialize(): Promise<void> {
    // Check if we have a stored key
    const storedKey = localStorage.getItem('pai_encryption_key');

    if (storedKey) {
      // Import the stored key
      const keyData = this.base64ToArrayBuffer(storedKey);
      this.encryptionKey = await crypto.subtle.importKey(
        'raw',
        keyData,
        { name: ALGORITHM, length: KEY_LENGTH },
        true,
        ['encrypt', 'decrypt']
      );
    } else {
      // Generate a new key
      this.encryptionKey = await crypto.subtle.generateKey(
        { name: ALGORITHM, length: KEY_LENGTH },
        true,
        ['encrypt', 'decrypt']
      );

      // Store the key for future use
      const exportedKey = await crypto.subtle.exportKey('raw', this.encryptionKey);
      const keyString = this.arrayBufferToBase64(exportedKey);
      localStorage.setItem('pai_encryption_key', keyString);
    }
  }

  /**
   * Encrypt data using AES-GCM
   */
  async encrypt(data: string): Promise<EncryptedData> {
    if (!this.encryptionKey) {
      await this.initialize();
    }

    if (!this.encryptionKey) {
      throw new Error('Encryption key not initialized');
    }

    // Generate a random IV
    const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));

    // Convert string to ArrayBuffer
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);

    // Encrypt the data
    const encryptedBuffer = await crypto.subtle.encrypt(
      {
        name: ALGORITHM,
        iv: iv,
        tagLength: TAG_LENGTH,
      },
      this.encryptionKey,
      dataBuffer
    );

    // Extract ciphertext and auth tag
    // In AES-GCM, the tag is appended to the ciphertext
    const encryptedArray = new Uint8Array(encryptedBuffer);
    const tagStart = encryptedArray.length - (TAG_LENGTH / 8);
    const ciphertext = encryptedArray.slice(0, tagStart);
    const tag = encryptedArray.slice(tagStart);

    return {
      ciphertext: this.arrayBufferToBase64(ciphertext),
      iv: this.arrayBufferToBase64(iv),
      tag: this.arrayBufferToBase64(tag),
    };
  }

  /**
   * Decrypt data using AES-GCM
   */
  async decrypt(encryptedData: EncryptedData): Promise<string> {
    if (!this.encryptionKey) {
      await this.initialize();
    }

    if (!this.encryptionKey) {
      throw new Error('Encryption key not initialized');
    }

    // Convert base64 strings back to ArrayBuffers
    const iv = this.base64ToArrayBuffer(encryptedData.iv);
    const ciphertext = this.base64ToArrayBuffer(encryptedData.ciphertext);
    const tag = this.base64ToArrayBuffer(encryptedData.tag);

    // Combine ciphertext and tag
    const encryptedBuffer = new Uint8Array(ciphertext.byteLength + tag.byteLength);
    encryptedBuffer.set(new Uint8Array(ciphertext), 0);
    encryptedBuffer.set(new Uint8Array(tag), ciphertext.byteLength);

    try {
      // Decrypt the data
      const decryptedBuffer = await crypto.subtle.decrypt(
        {
          name: ALGORITHM,
          iv: iv,
          tagLength: TAG_LENGTH,
        },
        this.encryptionKey,
        encryptedBuffer
      );

      // Convert ArrayBuffer back to string
      const decoder = new TextDecoder();
      return decoder.decode(decryptedBuffer);
    } catch (error) {
      console.error('Decryption failed:', error);
      throw new Error('Failed to decrypt data');
    }
  }

  /**
   * Clear encryption key (for logout/reset)
   */
  clearKey(): void {
    localStorage.removeItem('pai_encryption_key');
    this.encryptionKey = null;
  }

  /**
   * Convert ArrayBuffer to base64 string
   */
  private arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
    const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Convert base64 string to ArrayBuffer
   */
  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }
}

// Export singleton instance
export const encryptionManager = new EncryptionManager();
