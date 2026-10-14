0000000000001240 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1240:	mov    (%rdi),%rcx
    1243:	mov    0x8(%rdi),%rax
    1247:	sub    %rcx,%rax
    124a:	je     126a <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2a>
    124c:	sar    $0x2,%rax
    1250:	cmp    $0x1,%rax
    1254:	mov    %rax,%rdx
    1257:	adc    $0x0,%rdx
    125b:	cmp    $0x10,%rax
    125f:	jae    1271 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x31>
    1261:	xor    %esi,%esi
    1263:	xor    %eax,%eax
    1265:	jmp    131e <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xde>
    126a:	xor    %eax,%eax
    126c:	jmp    131a <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xda>
    1271:	mov    %rdx,%rsi
    1274:	and    $0xfffffffffffffff0,%rsi
    1278:	vpxor  %xmm0,%xmm0,%xmm0
    127c:	xor    %eax,%eax
    127e:	vpxor  %xmm1,%xmm1,%xmm1
    1282:	vpxor  %xmm2,%xmm2,%xmm2
    1286:	vpxor  %xmm3,%xmm3,%xmm3
    128a:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1299:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a8:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b7:	nopw   0x0(%rax,%rax,1)
    12c0:	vpmovsxdq (%rcx,%rax,4),%ymm4
    12c6:	vpaddq %ymm4,%ymm0,%ymm0
    12ca:	vpmovsxdq 0x10(%rcx,%rax,4),%ymm4
    12d1:	vpaddq %ymm4,%ymm1,%ymm1
    12d5:	vpmovsxdq 0x20(%rcx,%rax,4),%ymm4
    12dc:	vpmovsxdq 0x30(%rcx,%rax,4),%ymm5
    12e3:	vpaddq %ymm4,%ymm2,%ymm2
    12e7:	vpaddq %ymm5,%ymm3,%ymm3
    12eb:	add    $0x10,%rax
    12ef:	cmp    %rax,%rsi
    12f2:	jne    12c0 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x80>
    12f4:	vpaddq %ymm0,%ymm1,%ymm0
    12f8:	vpaddq %ymm0,%ymm2,%ymm0
    12fc:	vpaddq %ymm0,%ymm3,%ymm0
    1300:	vextracti128 $0x1,%ymm0,%xmm1
    1306:	vpaddq %xmm1,%xmm0,%xmm0
    130a:	vpshufd $0xee,%xmm0,%xmm1
    130f:	vpaddq %xmm1,%xmm0,%xmm0
    1313:	vmovq  %xmm0,%rax
    1318:	jmp    1328 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xe8>
    131a:	vzeroupper
    131d:	ret
    131e:	movslq (%rcx,%rsi,4),%rdi
    1322:	add    %rdi,%rax
    1325:	inc    %rsi
    1328:	cmp    %rsi,%rdx
    132b:	jne    131e <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xde>
    132d:	jmp    131a <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xda>
    132f:	nop
