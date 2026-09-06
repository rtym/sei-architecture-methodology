# Reference — Designing and documenting interfaces

Interfaces are architectural. ADD Step 5 defines them; every view packet's element catalog
(§2.3) references them; integrability, modifiability, and testability all hinge on them.

## Three things to remember

1. **All elements have interfaces** — an element that interacts with nothing has no reason to
   exist.
2. **Interfaces are two-way** — an interface is what an element **provides** *and* what it
   **requires** of its environment (resources, assumptions). If a required resource is missing
   or the environment misbehaves, the element cannot function.
3. **One interface can serve many actors** — and an element may deliberately expose **multiple
   interfaces** (separation of concerns; different access levels — public read-only vs.
   authenticated write; a separate admin/telemetry interface).

## Interface concepts

- **Resources** = **syntax** (the signature: name, argument names and types) + **semantics**
  (what invoking it does: value assignment, state changes incl. exceptional/partial-completion
  effects, events emitted, effect on future calls, humanly-observable results, whether it is
  atomic or interruptible). Without the semantics written down, an actor cannot safely use it.
- Provided resources are **operations** (transfer control + data, usually return a result, may
  fail), **events** (asynchronous; incoming = message/stream element to consume, outgoing =
  notify listeners), and **properties** (interface metadata — access rights, units of measure,
  formatting assumptions — that can change operation behaviour).
- **Interface evolution** — an interface is a contract; change it with care via:
  - **deprecation** (remove it; give long notice; optionally an error code announcing the
    removal date);
  - **versioning** (keep the old interface, add a new one; actors specify the version);
  - **extension** (leave the original untouched, add new resources; if the extension is
    incompatible, add an **internal interface + a mediator** that translates old ↔ new).

## Design principles

- **Principle of least surprise** — behave as the actor expects; name resources so the name
  hints at the use.
- **Small interfaces** — two interacting elements exchange as little as possible.
- **Uniform access** — don't leak implementation; a resource looks the same whether it returns
  from a cache, a computation, or a remote fetch.
- **Don't repeat yourself** — offer composable primitives, not many redundant ways to the same
  end.
- **Consistency** — one convention across the whole architecture for resource naming, parameter
  order, and error handling; follow the platform / language idioms developers expect.

## Four things a successful interface interaction must agree on

### 1. Interface scope

Which resources are directly available, to which actors. Constrain access for security,
performance management, or extensibility. The common pattern is a **gateway** (message gateway):
it translates actor requests into target-element requests, so it *becomes* the actor for the
target — useful when resource granularity differs from what actors need, when actors must be
restricted to a subset, or when the target's resources (number, protocol, type, location) will
change and the gateway can present a stable interface.

### 2. Interaction style

Driven by the communication/coordination mix and by co-located vs. remote deployment:
- **co-located** → efficient access to large data via shared memory;
- **available at the same time** → synchronous calls (RPC; **gRPC** = binary params,
  asynchronous, auth, bidirectional streaming, flow control, cancellation/timeouts, HTTP/2);
- **unreliable distributed environment** → asynchronous, event-based interactions over message
  queues or data streams.
- **REST** — six constraints: uniform interface (URIs, least surprise), client-server,
  **stateless** (auth carried in a token per request), cacheable, tiered (server split into
  independently deployable elements), code-on-demand (optional). HTTP command ↔ CRUD:
  `POST`→create, `GET`→read, `PUT`→update/replace, `PATCH`→update/modify, `DELETE`→delete.

### 3. Representation and structure of exchanged data

Converting internal data types to a wire format is *serialization / marshalling*. Choose a
representation by: **expressiveness** (arbitrary structures? trees? multilingual text?),
**interoperability** (does it match a standard the actors can parse — e.g. JSON?),
**performance** (bandwidth efficiency, parse complexity, prep time, cost), **implicit coupling**
(shared assumptions that break decoding), **transparency** (interceptable/observable — helps
debugging, hurts confidentiality). Common formats:
- **XML** — meta-language + schema; strong validation; verbose; costly to parse (must read whole
  document, sometimes multiple passes).
- **JSON** — name/value pairs + arrays; own schema language; far less verbose (field names once);
  parseable as read; efficient (types close to programming-language types).
- **Protocol Buffers** — binary, schema-defined (required/optional/nested), very compact; `.proto`
  compiled per language; mostly used with gRPC.

### 4. Error handling

Design for the non-nominal case explicitly. Strategies for an actor to learn something went
wrong: **exceptions** on failed operations · **status codes** (predefined, must be tested) ·
**properties** holding success/error state · **error events** (e.g. timeouts) for async
interactions · a readable **error log** stream. Common error sources the interface must handle
gracefully: invalid/illegal input (associate an error condition with the resource); the element
in the wrong state for the request; a required resource unavailable; a downstream call failing
or not returning. The exact set of exceptions/codes/events *is part of the interface*.

## Documenting the interface

Record, per significant element: the provided and required resources (syntax + semantics), the
interaction style, the data representation and structure, and the error model. Reference this
from ADD `Architecture.md` §8 and each V&B view packet §2.3 rather than duplicating it. Placing
the interface spec in a searchable store lets a reader trace how a value propagates across
elements.
