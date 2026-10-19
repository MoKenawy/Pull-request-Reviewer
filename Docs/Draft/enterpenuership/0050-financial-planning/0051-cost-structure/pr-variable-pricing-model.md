Done. With `eu-central-1`, EC2 still **TBD**, DynamoDB **On-Demand**, NLB, NAT Gateway, and public IPv4/EIP, we can now establish the **unit-cost sheet** without assuming any customer/review volume.

I’m treating prices as **USD list prices before taxes, discounts, Savings Plans/Reserved pricing, and account-specific credits**.

## Variable-resource cost structure

The master equation is:

\[
\boxed{
C_{AWS+AI}=\sum_i U_i\times P_i
}
\]

where \(U_i\) is actual resource usage and \(P_i\) is its unit price.

### 1. AI / OpenRouter

OpenRouter currently lists Qwen3.8 27B at **$0.0248 / 1M input tokens**, **$4.35 / 1M output tokens**, and **$0.0198 / 1M cache-read tokens**. The model was released August 14, 2026. [OpenRouter](https://openrouter.ai/qwen/qwen3.8-27b/?utm_source=chatgpt.com)

| Resource | Cost unit | Unit price |
|---|---:|---:|
| Qwen input | 1M tokens | **$0.0248** |
| Qwen output | 1M tokens | **$4.35** |
| Qwen cache read | 1M tokens | **$0.0198** |
| OpenRouter Standard platform fee | inference/platform spend | **5.5%** |

OpenRouter's current Standard pay-as-you-go plan lists a **5.5% platform fee**. [OpenRouter](https://openrouter.ai/pricing?utm_source=chatgpt.com)

Therefore:

\[
C_{Qwen}
=
0.0248\frac{T_{in}}{10^6}
+
4.35\frac{T_{out}}{10^6}
+
0.0198\frac{T_{cache}}{10^6}
\]

and, using Standard OpenRouter:

\[
C_{OpenRouter}
=
1.055\times C_{Qwen}
\]

assuming the 5.5% platform fee applies to the relevant spend.

---

# 2. EC2 — TBD

We're leaving the instance type deliberately unresolved.

AWS On-Demand EC2 is billed according to the time instances are running, with a 60-second minimum and then per-second billing. [AWS Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-on-demand-instances.html?utm_source=chatgpt.com)

So our unit is:

| Resource | Cost unit | Unit price |
|---|---:|---:|
| EC2 compute | instance-hour | **TBD** |
| EC2 compute | instance-second | **TBD** |

Formula:

\[
C_{EC2}
=
\sum_i H_iP_i
\]

No instance price enters the model until we choose the instance.

---

# 3. EBS

For the EC2 boot/data volume, `gp3` is the sensible baseline to price unless you later choose another volume class.

Current Frankfurt pricing references show:

| Resource | Cost unit | Unit price |
|---|---:|---:|
| EBS gp3 storage | GB-month | **$0.0952** |
| Additional gp3 IOPS | IOPS-month | **$0.006** |
| Additional gp3 throughput | MiB/s-month | **$0.0476** | :chatgpt-content-reference{index="3"}


So:

\[
C_{EBS}
=
GB_{storage}\times0.0952
+
IOPS_{extra}\times0.006
+
Throughput_{extra}\times0.0476
\]

The important point is that **gp3's included baseline performance means we don't automatically pay for every IOPS/throughput unit**.

---

# 4. Network Load Balancer

For Frankfurt, the pricing data shows:

| Resource | Cost unit | Unit price |
|---|---:|---:|
| NLB | NLB-hour | **$0.027** |
| NLB capacity | NLCU-hour | **$0.006** | :chatgpt-content-reference{index="4"}


AWS confirms an NLB has two billing dimensions: the load-balancer running time and consumed Network Load Balancer Capacity Units (NLCUs). [Amazon Web Services, Inc.](https://aws.amazon.com/elasticloadbalancing/pricing/?c=wa\&p=ft\&z=3\&utm_source=chatgpt.com)

Therefore:

\[
C_{NLB}
=
Hours_{NLB}\times0.027
+
NLCUHours\times0.006
\]

A useful reference point:

\[
730\times0.027=\boxed{\$19.71/month}
\]

for **one continuously running NLB**, before NLCU consumption.

That's not a usage assumption for the model; it's simply the normalized cost of one NLB-hour multiplied by a 730-hour accounting month.

---

# 5. Public IPv4 / Elastic IP

AWS currently charges:

\[
\boxed{\$0.005 / public\ IPv4-hour}
\]

for both in-use and idle public IPv4 addresses. [Amazon Web Services, Inc.](https://aws.amazon.com/vpc/pricing/?utm_source=chatgpt.com)

Therefore:

\[
C_{IPv4}
=
IPv4Count\times Hours\times0.005
\]

One continuously allocated IPv4:

\[
730\times0.005
=
\boxed{\$3.65/month}
\]

So we should not write "Elastic IP = $3.65/month" as a fixed cost; rather:

> **$0.005 per IP-hour × number of IPs × time**

because the number of public IPs is architectural.

---

# 6. NAT Gateway

This is one of the most important cost components.

Current Frankfurt pricing is:

| Resource | Cost unit | Unit price |
|---|---:|---:|
| NAT Gateway | NAT Gateway-hour | **$0.052** |
| NAT Gateway data processing | GB processed | **$0.052** |
| NAT Gateway public IPv4 | IP-hour | **$0.005** |

The Frankfurt-specific $0.052/hour and $0.052/GB figures are reflected in current pricing references, while AWS confirms that NAT Gateway billing consists of both gateway-hours and data processing per GB. [devop.sh](https://devop.sh/blog/aws-nat-gateway-hidden-cost/?utm_source=chatgpt.com)

Formula:

\[
C_{NAT}
=
H_{NAT}\times0.052
+
GB_{NAT}\times0.052
+
IPv4_{NAT}\times H\times0.005
\]

One continuously running NAT gateway:

\[
730\times0.052
=
\boxed{\$37.96/month}
\]

**before any data processing.**

This is important for your model because NAT is both:

```text
capacity cost
+
usage cost
```

---

# 7. Internet data transfer

We should not simply create a generic "network = negligible" line anymore.

AWS currently gives the first **100 GB/month of Internet data transfer out** free, aggregated across AWS services/regions, then the common first-tier rate is **$0.09/GB** for the next 10 TB/month. AWS also states that data transfer into EC2 from the Internet is free. [Amazon Web Services, Inc.](https://aws.amazon.com/ec2/pricing/on-demand-backup/?utm_source=chatgpt.com)

So:

| Traffic | Unit price |
|---|---:|
| Internet → AWS | **$0/GB** |
| AWS → Internet | **$0.09/GB** after applicable free tier |
| Same-AZ AWS data transfer | **$0/GB** |
| Cross-AZ regional transfer | **$0.01/GB each direction** |

AWS specifically notes that data transferred between EC2 and certain AWS services in the same Region can be free when transferred directly, while services such as NAT Gateway can introduce their own processing charges. [Amazon Web Services, Inc.](https://aws.amazon.com/ec2/pricing/on-demand-backup/?utm_source=chatgpt.com)

This means we should model network traffic **by path**, not simply by "GB of network."

---

# 8. S3

For S3 Standard in Frankfurt:

| Resource | Cost unit | Unit price |
|---|---:|---:|
| S3 Standard storage | GB-month | **$0.0245** |
| PUT/COPY/POST/LIST | 1K requests | **$0.0054** |
| GET/SELECT/other | 1K requests | **$0.00043** |
| Internet egress | GB | standard AWS transfer pricing |

Current regional pricing references put Frankfurt S3 Standard storage at $0.0245/GB-month and request pricing at $0.0054/1K write-type requests and $0.00043/1K GET-type requests. [DEV Community](https://dev.to/nahuel990/ministack-now-emulates-mwaa-develop-and-test-airflow-dags-locally-skip-the-353month-2ehp?utm_source=chatgpt.com)

AWS's own S3 documentation confirms that S3 billing separates storage, requests/retrievals, and data transfer. [Amazon Web Services, Inc.](https://aws.amazon.com/s3/pricing/)

So:

\[
C_{S3}
=
GB_{stored}\times0.0245
+
\frac{PUT+COPY+POST+LIST}{1000}\times0.0054
+
\frac{GET+SELECT+Other}{1000}\times0.00043
+
C_{S3-transfer}
\]

---

# 9. DynamoDB — On-Demand

Your choice of On-Demand gives us a clean request-based model.

Current Frankfurt rates are approximately:

| Resource | Cost unit | Unit price |
|---|---:|---:|
| Read | 1M RRU | **$0.1525** |
| Write | 1M WRU | **$0.7625** |
| Storage | GB-month | **$0.306** |

These Frankfurt rates are currently listed from AWS public-pricing data by pricing references synchronized with the AWS pricing API. [dynobase.dev](https://dynobase.dev/dynamodb-pricing-calculator/?utm_source=chatgpt.com)

AWS defines the actual metering:

- reads consume **RRUs in 4 KB increments**
- writes consume **WRUs in 1 KB increments**
- transactional operations consume more units
- storage is billed separately. [Amazon Web Services, Inc.](https://aws.amazon.com/dynamodb/pricing/?utm_source=chatgpt.com)

Therefore:

\[
C_{DDB}
=
\frac{RRU}{10^6}\times0.1525
+
\frac{WRU}{10^6}\times0.7625
+
GB_{stored}\times0.306
\]

This is significantly better for our model than "DynamoDB = $X/customer."

---

# 10. IAM

IAM itself contributes:

\[
\boxed{C_{IAM}=0}
\]

AWS states that IAM is available at no additional charge. [AWS Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-iam.html?utm_source=chatgpt.com)

So:

| Resource | Unit cost |
|---|---:|
| IAM users | **$0** |
| IAM roles | **$0** |
| IAM policies | **$0** |

The services accessed using those credentials still generate their normal costs.

---

# 11. Auto Scaling Groups

Also:

\[
\boxed{C_{ASG}=0}
\]

AWS explicitly says there is **no additional charge for Auto Scaling**; you pay for the resources it launches and applicable CloudWatch charges. [Amazon Web Services, Inc.](https://aws.amazon.com/autoscaling/pricing/?utm_source=chatgpt.com)

So:

```text
ASG
  │
  ├── EC2 instance-hours → paid
  └── scaling mechanism   → $0
```

---

# 12. The resulting unit-cost sheet

This is the version I'd put into the financial-plan document:

| Category | Resource | Billing unit | Unit cost |
|---|---|---:|---:|
| **AI** | Qwen input | 1M tokens | **$0.0248** |
| | Qwen output | 1M tokens | **$4.35** |
| | Qwen cache-read | 1M tokens | **$0.0198** |
| | OpenRouter Standard | inference/platform spend | **5.5%** |
| **Compute** | EC2 | instance-hour | **TBD** |
| | EBS gp3 | GB-month | **$0.0952** |
| | EBS extra IOPS | IOPS-month | **$0.006** |
| | EBS extra throughput | MiB/s-month | **$0.0476** |
| **Load balancing** | NLB | NLB-hour | **$0.027** |
| | NLB | NLCU-hour | **$0.006** |
| **Networking** | Public IPv4 | IP-hour | **$0.005** |
| | NAT Gateway | gateway-hour | **$0.052** |
| | NAT Gateway | GB processed | **$0.052** |
| | Internet egress | GB | **$0.09** after applicable free tier |
| | Cross-AZ transfer | GB/direction | **$0.01** |
| **S3** | Standard storage | GB-month | **$0.0245** |
| | PUT/COPY/POST/LIST | 1K requests | **$0.0054** |
| | GET/SELECT/other | 1K requests | **$0.00043** |
| **Database** | DynamoDB read | 1M RRU | **$0.1525** |
| | DynamoDB write | 1M WRU | **$0.7625** |
| | DynamoDB storage | GB-month | **$0.306** |
| **Identity** | IAM | — | **$0** |
| **Scaling** | Auto Scaling | — | **$0** |

---

# 13. Our actual economic equation

So instead of:

\[
Cost/Review
\]

we now have:

\[
\boxed{
C =
C_{LLM}
+C_{EC2}
+C_{EBS}
+C_{NLB}
+C_{NAT}
+C_{IPv4}
+C_{Transfer}
+C_{S3}
+C_{DDB}
}
\]

Expanded:

\[
\begin{aligned}
C={}&
T_{in}(0.0248/10^6)
+T_{out}(4.35/10^6)
+T_{cache}(0.0198/10^6)\\
&+EC2_{hours}P_{EC2}\\
&+EBS_{GB}(0.0952)\\
&+NLB_{hours}(0.027)
+NLCU_{hours}(0.006)\\
&+NAT_{hours}(0.052)
+NAT_{GB}(0.052)\\
&+IPv4_{hours}(0.005)\\
&+Internet_{GB}(0.09)\\
&+CrossAZ_{GB}(0.01)\\
&+S3_{storage}(0.0245)\\
&+S3_{writeRequests}(0.0054/1000)\\
&+S3_{readRequests}(0.00043/1000)\\
&+DDB_{RRU}(0.1525/10^6)\\
&+DDB_{WRU}(0.7625/10^6)\\
&+DDB_{storage}(0.306)
\end{aligned}
\]

Then:

\[
\boxed{\text{Customer Price} = C + \text{Markup}}
\]

That's the clean **pass-through / variable-cost-matching foundation** we were looking for.

## One important architectural implication

Your most interesting cost paths are now visible:

```text
                    ┌──────────────┐
                    │ Qwen/OpenRouter
                    │ token usage
                    └──────┬───────┘
                           │
                        NAT GB
                           │
Internet ──► NLB ──► EC2 ──┘
              │
              └── NLCU

EC2 ──► DynamoDB
       ├── RRU
       ├── WRU
       └── GB-month

EC2 ──► S3
       ├── Requests
       ├── GB-month
       └── Transfer
```

And there is a particularly important optimization implication: **S3 and DynamoDB can use gateway VPC endpoints, avoiding NAT Gateway processing for those AWS-service paths.** AWS explicitly notes that gateway endpoints for S3 have no hourly/data-processing charge and can avoid NAT processing costs. [Amazon Web Services, Inc.](https://aws.amazon.com/vpc/pricing/?did=ap_card\&utm_source=chatgpt.com)

That means our financial model should **not automatically charge all EC2→S3/DynamoDB traffic through NAT**. The eventual architecture can materially change the variable cost.

### What remains intentionally unresolved

Only a few things are still `TBD` rather than guessed:

| Item | Why |
|---|---|
| EC2 instance-hour price | Instance type not selected |
| Exact EBS configuration | Volume size / extra performance not selected |
| Number of NAT gateways | AZ/HA topology not selected |
| Number of public IPv4s | Depends on exact topology |
| CloudWatch | Logging/metrics configuration not yet specified |
| ECR | Needed only if your deployment uses ECR |
| Secrets Manager | Needed only if you choose it |
| Route 53 | Needed only if you use Route 53 |
| GitHub-side costs | External to AWS |

One caveat: some regional figures above come from current pricing datasets/calculators synchronized from AWS's public pricing data rather than a directly queryable regional AWS table; AWS's official pages confirm the billing dimensions and pricing structure. For the financial plan, I would mark those as **"current market/reference price — verify with AWS Pricing Calculator before committing cash."**