import { VectorSearch } from '../lib/vector-search';

describe('VectorSearch', () => {
  let vectorSearch: VectorSearch;

  beforeAll(() => {
    vectorSearch = new VectorSearch();
  });

  describe('generateEmbedding', () => {
    it('should generate embedding vector', async () => {
      const text = 'This is a test sentence';
      const embedding = await vectorSearch.generateEmbedding(text);

      expect(embedding).toBeInstanceOf(Array);
      expect(embedding.length).toBe(384);
      expect(embedding.every(val => typeof val === 'number')).toBe(true);
    });

    it('should generate normalized embeddings', async () => {
      const text = 'Test normalization';
      const embedding = await vectorSearch.generateEmbedding(text);

      // Check that the embedding is normalized (L2 norm should be close to 1)
      const norm = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
      expect(norm).toBeCloseTo(1, 5);
    });

    it('should generate different embeddings for different texts', async () => {
      const embedding1 = await vectorSearch.generateEmbedding('First text');
      const embedding2 = await vectorSearch.generateEmbedding('Second text');

      expect(embedding1).not.toEqual(embedding2);
    });
  });

  describe('storeWithEmbedding', () => {
    it('should create knowledge item with embedding', async () => {
      const item = await vectorSearch.storeWithEmbedding(
        'test-id',
        'test-category',
        'This is test content',
        { source: 'test' }
      );

      expect(item.id).toBe('test-id');
      expect(item.category).toBe('test-category');
      expect(item.content).toBe('This is test content');
      expect(item.embedding).toBeInstanceOf(Array);
      expect(item.embedding.length).toBe(384);
      expect(item.metadata).toEqual({ source: 'test' });
      expect(item.timestamp).toBeDefined();
    });
  });
});
