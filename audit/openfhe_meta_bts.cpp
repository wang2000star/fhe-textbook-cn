// BSD 2-Clause License
// Copyright (c) 2014-2022, NJIT, Duality Technologies Inc. and other contributors
// Copyright (c) 2026, fhe-textbook-cn academic review contributors
// All rights reserved.
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
// 1. Redistributions of source code must retain the above copyright notice,
//    this list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//
// Context/API setup adapted from OpenFHE v1.6.1's official example:
// src/pke/examples/iterative-ckks-bootstrapping.cpp
// Upstream commit: b59e1f291965f14fbee5172cd83a20f5b856204f
// Numerical experiment with HEStd_NotSet; this is not a security profile.
// EvalBootstrap uses public evaluation keys. Secret-key decryption below is
// only an offline calibration/measurement oracle, outside that evaluator.

#include "openfhe.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <complex>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

using namespace lbcrypto;
using Values = std::vector<std::complex<double>>;

double MaxError(const Values& x, const Values& y) {
    if (x.size() != y.size())
        throw std::runtime_error("different slot counts");
    double result = 0.0;
    for (size_t i = 0; i < x.size(); ++i) {
        const double e = std::abs(x[i] - y[i]);
        if (!std::isfinite(e))
            throw std::runtime_error("non-finite slot error");
        result = std::max(result, e);
    }
    return result;
}

double MeanError(const Values& x, const Values& y) {
    double result = 0.0;
    for (size_t i = 0; i < x.size(); ++i)
        result += std::abs(x[i] - y[i]);
    return result / x.size();
}

void PrintValues(const Values& values) {
    std::cout << '[';
    for (size_t i = 0; i < values.size(); ++i) {
        if (i)
            std::cout << ',';
        std::cout << '[' << values[i].real() << ',' << values[i].imag() << ']';
    }
    std::cout << ']';
}

Values DecryptForMeasurement(const CryptoContext<DCRTPoly>& cc, const PrivateKey<DCRTPoly>& sk,
                             const Ciphertext<DCRTPoly>& ct, uint32_t slots) {
    Plaintext result;
    cc->Decrypt(sk, ct, &result);
    result->SetLength(slots);
    return result->GetCKKSPackedValue();
}

int main() {
    try {
        std::cout << std::setprecision(17);
        constexpr uint32_t slots = 8;
        constexpr uint32_t remaining = 10;
        const std::vector<uint32_t> budget = {3, 3};
        const auto secretDistribution = UNIFORM_TERNARY;
        const uint32_t depth = remaining + FHECKKSRNS::GetBootstrapDepth(budget, secretDistribution) + 1;
        CCParams<CryptoContextCKKSRNS> parameters;
        parameters.SetSecretKeyDist(secretDistribution);
        parameters.SetSecurityLevel(HEStd_NotSet);
        parameters.SetRingDim(4096);
        parameters.SetScalingModSize(59);
        parameters.SetFirstModSize(60);
        parameters.SetScalingTechnique(FLEXIBLEAUTO);
        parameters.SetMultiplicativeDepth(depth);
        const auto cc = GenCryptoContext(parameters);
        for (auto capability : {PKE, KEYSWITCH, LEVELEDSHE, ADVANCEDSHE, FHE})
            cc->Enable(capability);
        cc->EvalBootstrapSetup(budget, {0, 0}, slots);
        const auto keys = cc->KeyGen();
        cc->EvalMultKeyGen(keys.secretKey);
        cc->EvalBootstrapKeyGen(keys.secretKey, slots);
        auto encrypt = [&](const std::vector<double>& x) {
            auto plaintext = cc->MakeCKKSPackedPlaintext(x, 1, depth - 1, nullptr, slots);
            return cc->Encrypt(keys.publicKey, plaintext);
        };

        // Offline calibration uses a separate ciphertext and fixed known input.
        auto calibration = encrypt({0.03125, -0.0625, 0.1875, -0.3125, 0.5625, -0.6875, 0.8125, -0.9375});
        const auto calibrationInput = DecryptForMeasurement(cc, keys.secretKey, calibration, slots);
        const auto calibrationOut = cc->EvalBootstrap(calibration);
        const double calibrationError = MaxError(
            DecryptForMeasurement(cc, keys.secretKey, calibrationOut, slots), calibrationInput);
        if (!(calibrationError > 0.0 && calibrationError < 0.5))
            throw std::runtime_error("calibration outside the intended numerical range");
        // A five-bit empirical buffer is not a worst-case input-bound proof.
        // Keep the implementation's uint32_t shift strictly in range.
        const uint32_t precision = static_cast<uint32_t>(
            std::max(1, std::min(25, static_cast<int>(std::floor(-std::log2(calibrationError))) - 5)));
        std::cout << "DATA {\"type\":\"parameters\",\"ring_dimension\":4096,\"slots\":8,"
                  << "\"security_level\":\"HEStd_NotSet\",\"native_bits\":64,"
                  << "\"secret_distribution\":\"UNIFORM_TERNARY\",\"scaling\":\"FLEXIBLEAUTO\","
                  << "\"scaling_modulus_bits\":59,\"first_modulus_bits\":60,"
                  << "\"level_budget\":[3,3],\"depth\":" << depth
                  << ",\"calibration_max_error\":" << calibrationError
                  << ",\"precision_argument\":" << precision << "}\n";

        const std::vector<std::vector<double>> messages = {
            {-0.875, -0.5, -0.125, 0.0, 0.125, 0.375, 0.75, 0.9375},
            {-0.875, -0.5, -0.125, 0.0, 0.125, 0.375, 0.75, 0.9375},
            {-0.91, 0.83, -0.17, 0.29, 1.0 / 3.0, -2.0 / 7.0, 0.02, 0.99}};
        const std::vector<double> perturbations = {0.0, std::ldexp(1.0, -10), 0.0};
        bool acceptable = true;
        for (size_t caseIndex = 0; caseIndex < messages.size(); ++caseIndex) {
            const auto& message = messages[caseIndex];
            auto represented = message;
            for (auto& x : represented)
                x += perturbations[caseIndex];
            const Values target(message.begin(), message.end());
            const Values encodedTarget(represented.begin(), represented.end());
            const auto input = encrypt(represented);
            const auto inputValue = DecryptForMeasurement(cc, keys.secretKey, input, slots);
            const auto start = std::chrono::steady_clock::now();
            const auto first = cc->EvalBootstrap(input);
            const auto middle = std::chrono::steady_clock::now();
            const auto twice = cc->EvalBootstrap(input, 2, precision);
            const auto end = std::chrono::steady_clock::now();
            const auto firstValue = DecryptForMeasurement(cc, keys.secretKey, first, slots);
            const auto twiceValue = DecryptForMeasurement(cc, keys.secretKey, twice, slots);
            const double error1 = MaxError(firstValue, inputValue);
            const double error2 = MaxError(twiceValue, inputValue);
            const int remainingAfter = static_cast<int>(depth) - static_cast<int>(twice->GetLevel()) -
                                       (static_cast<int>(twice->GetNoiseScaleDeg()) - 1);
            // These tolerances define this experiment, not all CKKS parameters.
            acceptable = acceptable && error1 < 1e-4 && error2 < 1e-6 && error2 < error1 && remainingAfter > 0;
            if (perturbations[caseIndex] != 0.0)
                acceptable = acceptable && MaxError(twiceValue, target) > perturbations[caseIndex] / 2;
            std::cout << "DATA {\"type\":\"case\",\"case_index\":" << caseIndex
                      << ",\"represented_perturbation\":" << perturbations[caseIndex]
                      << ",\"input_encoding_encryption_max_error\":" << MaxError(inputValue, encodedTarget)
                      << ",\"input_error_to_unperturbed_target\":" << MaxError(inputValue, target)
                      << ",\"one_iteration_max_added_error\":" << error1
                      << ",\"two_iterations_max_added_error\":" << error2
                      << ",\"one_iteration_mean_added_error\":" << MeanError(firstValue, inputValue)
                      << ",\"two_iterations_mean_added_error\":" << MeanError(twiceValue, inputValue)
                      << ",\"two_iterations_error_to_unperturbed_target\":" << MaxError(twiceValue, target)
                      << ",\"one_iteration_max_error_bits\":" << -std::log2(error1)
                      << ",\"two_iterations_max_error_bits\":" << -std::log2(error2)
                      << ",\"input_towers\":" << input->GetElements()[0].GetNumOfElements()
                      << ",\"output_towers\":" << twice->GetElements()[0].GetNumOfElements()
                      << ",\"input_scale\":" << input->GetScalingFactor()
                      << ",\"output_scale\":" << twice->GetScalingFactor()
                      << ",\"levels_remaining\":" << remainingAfter
                      << ",\"one_iteration_seconds\":" << std::chrono::duration<double>(middle - start).count()
                      << ",\"two_iterations_seconds\":" << std::chrono::duration<double>(end - middle).count()
                      << ",\"input_decoded\":";
            PrintValues(inputValue);
            std::cout << ",\"output_one_decoded\":";
            PrintValues(firstValue);
            std::cout << ",\"output_two_decoded\":";
            PrintValues(twiceValue);
            std::cout << "}\n";
        }
        bool rejectsThree = false;
        try {
            cc->EvalBootstrap(calibration, 3, precision);
        } catch (const std::exception&) {
            rejectsThree = true;
        }
        std::cout << "DATA {\"type\":\"checks\",\"configured_cases_pass\":"
                  << (acceptable ? "true" : "false") << ",\"rejects_three_iterations\":"
                  << (rejectsThree ? "true" : "false") << "}\n";
        return acceptable && rejectsThree ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "Experiment failed: " << error.what() << '\n';
        return 2;
    }
}
