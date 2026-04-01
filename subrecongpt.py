import openai
import dns.resolver
import argparse
import sys
import time
from os import popen


def generate_subdomains(subdomain, domain, api_key=None, mode=None):
    openai.api_key = api_key
    if mode == 'openai':
        print("Here")
        while True:  # Continue trying until a successful API call is made
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"Generate 5 subdomains similar to {subdomain}."},
                    ],
                )
                ai_generated_subdomains = [f"{sub}.{domain}" for sub in response['choices'][0]['message']['content'].strip().split('\n')]

                return ai_generated_subdomains
            except openai.error.RateLimitError as e:
                print("Rate limit exceeded. Sleeping for 20 seconds...")
                time.sleep(20)  # Sleep for 20 seconds and then try again
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise e  # If it's a different kind of error, raise it
    else:
        subdomains = popen(f"opencode run 'Generate exactly 10 subdomains based on \"{subdomain}\" and return full domain names like subdomain.{domain}. Do not return only the subdomain part. Output only one full domain per line, no explanations or extra text.'").read()
        print(subdomains)
        ai_generated_subdomains = [line.strip() for line in subdomains.splitlines() if line.strip()]
        return ai_generated_subdomains

def resolve_subdomains(subdomains):
    resolved_subdomains = []
    for subdomain in subdomains:
        try:
            answers = dns.resolver.resolve(subdomain, 'A')
            for rdata in answers:
                resolved_subdomains.append(subdomain)
                print(f"\n*** {subdomain} RESOLVES to {rdata.address} ***\n")
        except dns.resolver.NXDOMAIN:
            print(f"{subdomain} does not resolve.")
        except Exception as e:
            print(f"Error resolving {subdomain}: {e}")

    return resolved_subdomains

def main():
    parser = argparse.ArgumentParser(description='AI-assisted subdomain discovery.')
    parser.add_argument('--apikey', required=False, help='OpenAI API key.')
    parser.add_argument('--mode', required=False, help='AI selection mode.')
    args = parser.parse_args()

    lines = [line.strip() for line in sys.stdin]


    for line in lines:
        if '*' in line:  # Skip wildcard domains
            continue
        subdomain, domain = line.split('.', 1)  # Split the line into subdomain and domain
        print(f"\nSubdomain = {subdomain}.{domain}")
        new_subdomains = generate_subdomains(subdomain, domain, mode=args.mode, api_key=args.apikey )
        print(new_subdomains)
        print(f"Guesses: {', '.join([sub.split('.')[0] for sub in new_subdomains])}\n")
        resolved_subdomains = resolve_subdomains(new_subdomains)
        time.sleep(1)  # Pause for 1 second



if __name__ == "__main__":
    main()
