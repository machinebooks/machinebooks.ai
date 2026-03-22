# Extraído de: LibroFinOps/cap-08-routing-modelos.md
-- Configuración de routing para los servicios principales
INSERT INTO llm_service_config VALUES
  ('document_classifier',   'fast',     FALSE, TRUE,  '256',  NOW(), 'arquitecto'),
  ('field_extractor',       'fast',     FALSE, TRUE,  '512',  NOW(), 'arquitecto'),
  ('summary_generator',     'balanced', FALSE, TRUE,  '1024', NOW(), 'arquitecto'),
  ('proposal_section',      'balanced', TRUE,  FALSE, '2048', NOW(), 'arquitecto'),
  ('risk_evaluator',        'powerful', FALSE, FALSE, '4096', NOW(), 'arquitecto'),
  ('offer_generator',       'powerful', FALSE, FALSE, '8192', NOW(), 'arquitecto'),
  ('chat_assistant',        'balanced', TRUE,  TRUE,  '2048', NOW(), 'arquitecto');
