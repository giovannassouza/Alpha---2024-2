def validate_cpf(cpf: str) -> bool:
    # Step 1: Clean the CPF (remove non-numeric characters)
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Step 2: Check length and invalid patterns
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Step 3: Calculate the first check digit
    def calculate_digit(cpf_part):
        weight = len(cpf_part) + 1
        total = sum(int(digit) * (weight - idx) for idx, digit in enumerate(cpf_part))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    first_digit = calculate_digit(cpf[:9])
    second_digit = calculate_digit(cpf[:9] + str(first_digit))

    # Step 4: Validate against provided check digits
    return cpf == cpf[:9] + str(first_digit) + str(second_digit)

print(validate_cpf("111.111.111-11"))
print(validate_cpf("523.116.878-59"))
print(validate_cpf("123.456.789-10"))