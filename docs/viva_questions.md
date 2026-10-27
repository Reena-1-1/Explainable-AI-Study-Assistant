StudyLens AI — Viva Questions and Answers

1. What is StudyLens AI?

StudyLens AI is an Explainable AI Study Assistant designed to answer questions based on uploaded PDF documents. It aims to provide answers with supporting evidence and page references so users can verify the information.

2. What problem does this project solve?

Finding specific information in lengthy PDFs can take time. StudyLens AI aims to make document-based question answering easier by retrieving relevant passages and generating answers from them.

3. What is RAG?

RAG stands for Retrieval-Augmented Generation. It retrieves relevant information from a document and provides that information to a language model to help generate an answer.

4. Why do we use FAISS?

FAISS is a library used for efficient similarity search over vectors. In our project, it helps retrieve text chunks that are semantically relevant to a user's question.

5. What are embeddings?

Embeddings are numerical representations of text. They help the system compare the meaning of a question with the meaning of document passages.

6. What is chunking?

Chunking divides a long document into smaller pieces of text. This allows the retrieval system to search for relevant passages instead of processing the entire document as one large block.

7. What is chunk overlap?

Chunk overlap means repeating a small portion of text between neighbouring chunks. It helps preserve context when a sentence or idea crosses a chunk boundary.

8. How does the system process a PDF?

The intended workflow extracts text from the PDF, divides it into chunks, creates embeddings, retrieves relevant chunks using FAISS, and passes the retrieved context to a language model to generate an answer.

9. What is explainability in this project?

Explainability means helping users understand and verify an answer by showing supporting document evidence and page references, where these features are available.

10. How does the project try to reduce hallucinations?

The system is designed to provide the language model with relevant passages retrieved from the uploaded document. Evidence and page references also help users check answers. However, this cannot guarantee that every answer is correct.

11. What is SQLite?

SQLite is a lightweight relational database that stores information in a database file. Our documentation specifies a "qa_history" table for storing questions, answers, document names, timestamps, cited pages, and retrieval scores; actual integration must be verified.

12. What is the purpose of the "qa_history" table?

The proposed "qa_history" table stores details of question-and-answer interactions. This can support reviewing previous questions and answers if history storage and display are implemented in the application.

13. What is the role of the embedding model?

The project uses Sentence Transformers with the "all-MiniLM-L6-v2" model to convert text into vector representations. These vectors support similarity-based retrieval.

14. What are the limitations of the project?

The system may retrieve irrelevant passages or generate incorrect answers. Scanned PDFs may not work without OCR support, and performance can depend on document quality, model loading, and API availability.

15. What improvements can be made in the future?

Possible improvements include OCR for scanned PDFs, better evaluation of answer accuracy, improved retrieval, and additional document support. These should be treated as future enhancements unless they are implemented and tested.