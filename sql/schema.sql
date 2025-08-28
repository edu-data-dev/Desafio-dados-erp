-- Tabela principal para armazenar cada pedido/conta.
-- Centraliza as informações mestras de cada transação.
CREATE TABLE IF NOT EXISTS guest_checks (
    guest_check_id BIGINT PRIMARY KEY,
    location_ref VARCHAR(255) NOT NULL,
    check_number INT,
    is_closed BOOLEAN DEFAULT FALSE,
    guest_count INT,
    subtotal DECIMAL(10, 2),
    check_total DECIMAL(10, 2),
    discount_total DECIMAL(10, 2),
    payment_total DECIMAL(10, 2),
    table_number INT,
    employee_number INT,
    opened_at_utc TIMESTAMP,
    closed_at_utc TIMESTAMP,
    last_transaction_at_utc TIMESTAMP,
    last_updated_at_utc TIMESTAMP
);

-- Tabela para os impostos aplicados em cada pedido.
-- Relação N-para-1 com guest_checks, permitindo múltiplos impostos por pedido.
CREATE TABLE IF NOT EXISTS guest_check_taxes (
    id SERIAL PRIMARY KEY, -- Usamos uma chave primária substituta para facilitar referências.
    guest_check_id BIGINT NOT NULL REFERENCES guest_checks(guest_check_id),
    tax_number INT NOT NULL,
    taxable_sales_total DECIMAL(10, 2),
    tax_collected_total DECIMAL(10, 2),
    tax_rate DECIMAL(5, 2),
    tax_type INT,
    UNIQUE(guest_check_id, tax_number) -- Garante que o mesmo imposto não seja adicionado duas vezes ao mesmo pedido.
);

-- Tabela para as linhas de detalhe de um pedido.
-- Esta tabela é o coração do pedido, listando tudo que foi consumido, descontos, etc.
-- O desafio menciona que ela pode conter menuItem, discount, serviceCharge, etc.
-- Por isso, usamos uma coluna 'line_type' para identificar o que cada linha representa.
CREATE TABLE IF NOT EXISTS detail_lines (
    guest_check_line_item_id BIGINT PRIMARY KEY,
    guest_check_id BIGINT NOT NULL REFERENCES guest_checks(guest_check_id),
    line_number INT,
    line_type VARCHAR(50) NOT NULL, -- Ex: 'MENU_ITEM', 'DISCOUNT', 'SERVICE_CHARGE'
    display_total DECIMAL(10, 2),
    display_quantity INT,

    -- Chave estrangeira para um futuro mestre de itens de menu (pode ser nula se a linha for um desconto)
    menu_item_number INT,
    -- No futuro, poderíamos ter:
    -- discount_id INT REFERENCES discounts(id),
    -- service_charge_id INT REFERENCES service_charges(id),

    detail_at_utc TIMESTAMP,
    last_updated_at_utc TIMESTAMP
);

-- Tabela Mestre de Itens do Cardápio (opcional, mas boa prática)
-- Centraliza as informações dos produtos, evitando repetição.
CREATE TABLE IF NOT EXISTS menu_items (
    menu_item_number INT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2)
);