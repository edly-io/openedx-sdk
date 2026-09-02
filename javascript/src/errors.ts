export class OpenEdxSdkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'OpenEdxSdkError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class AuthenticationError extends OpenEdxSdkError {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class ApiError extends OpenEdxSdkError {
  readonly status: number | null;

  readonly body: unknown;

  constructor(status: number | null, message: string, body: unknown = null) {
    super(`HTTP ${status ?? 'ERR'}: ${message}`);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}
