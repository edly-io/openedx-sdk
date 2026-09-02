import { booleanParam, compactParams, joinUrl, stripTrailingSlash } from '../http';

describe('http helpers', () => {
  it('strips trailing slashes', () => {
    expect(stripTrailingSlash('https://a.com/')).toBe('https://a.com');
    expect(stripTrailingSlash('https://a.com///')).toBe('https://a.com');
    expect(stripTrailingSlash('https://a.com')).toBe('https://a.com');
  });

  it('joins a base and a path', () => {
    expect(joinUrl('https://a.com/', '/api/x')).toBe('https://a.com/api/x');
  });

  it('drops undefined and null params', () => {
    expect(compactParams({ a: 1, b: undefined, c: null })).toEqual({ a: 1 });
  });

  it('returns undefined when every param is empty', () => {
    expect(compactParams({ a: undefined })).toBeUndefined();
  });

  it('serializes booleans the way the API expects', () => {
    expect(booleanParam(true)).toBe('true');
    expect(booleanParam(false)).toBe('false');
    expect(booleanParam(undefined)).toBeUndefined();
  });
});
