0000000000001220 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m>:
    1220:	test   %rcx,%rcx
    1223:	je     12f8 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xd8>
    1229:	push   %rbp
    122a:	push   %r15
    122c:	push   %r14
    122e:	push   %r13
    1230:	push   %r12
    1232:	push   %rbx
    1233:	mov    (%rsi),%rax
    1236:	mov    %rax,-0x8(%rsp)
    123b:	mov    (%rdx),%rdx
    123e:	mov    (%rdi),%rsi
    1241:	mov    %rcx,%rdi
    1244:	and    $0xfffffffffffffffe,%rdi
    1248:	lea    0x4(%rdx),%r8
    124c:	lea    0x0(,%rcx,4),%r9
    1254:	lea    0x4(%rsi),%r10
    1258:	xor    %r11d,%r11d
    125b:	jmp    126f <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x4f>
    125d:	nopl   (%rax)
    1260:	inc    %r11
    1263:	add    %r9,%r10
    1266:	cmp    %rcx,%r11
    1269:	je     12ee <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xce>
    126f:	mov    %r11,%r14
    1272:	imul   %rcx,%r14
    1276:	mov    -0x8(%rsp),%rax
    127b:	lea    (%rax,%r14,4),%rbx
    127f:	lea    (%rsi,%r14,4),%r14
    1283:	mov    %r8,%r15
    1286:	xor    %eax,%eax
    1288:	jmp    129b <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x7b>
    128a:	nopw   0x0(%rax,%rax,1)
    1290:	inc    %rax
    1293:	add    %r9,%r15
    1296:	cmp    %rcx,%rax
    1299:	je     1260 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x40>
    129b:	mov    (%rbx,%rax,4),%ebp
    129e:	xor    %r13d,%r13d
    12a1:	cmp    $0x1,%rcx
    12a5:	je     12d3 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0xb3>
    12a7:	nopw   0x0(%rax,%rax,1)
    12b0:	mov    -0x4(%r15,%r13,4),%r12d
    12b5:	imul   %ebp,%r12d
    12b9:	add    %r12d,-0x4(%r10,%r13,4)
    12be:	mov    (%r15,%r13,4),%r12d
    12c2:	imul   %ebp,%r12d
    12c6:	add    %r12d,(%r10,%r13,4)
    12ca:	add    $0x2,%r13
    12ce:	cmp    %r13,%rdi
    12d1:	jne    12b0 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x90>
    12d3:	test   $0x1,%cl
    12d6:	je     1290 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
    12d8:	mov    %rax,%r12
    12db:	imul   %rcx,%r12
    12df:	lea    (%rdx,%r12,4),%r12
    12e3:	imul   (%r12,%r13,4),%ebp
    12e8:	add    %ebp,(%r14,%r13,4)
    12ec:	jmp    1290 <_Z15kern_k08_matmulRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_m+0x70>
    12ee:	pop    %rbx
    12ef:	pop    %r12
    12f1:	pop    %r13
    12f3:	pop    %r14
    12f5:	pop    %r15
    12f7:	pop    %rbp
    12f8:	ret
    12f9:	nopl   0x0(%rax)
