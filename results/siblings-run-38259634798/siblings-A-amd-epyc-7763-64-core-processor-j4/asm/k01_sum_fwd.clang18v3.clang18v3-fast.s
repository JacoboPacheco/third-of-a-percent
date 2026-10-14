0000000000001220 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1220:	mov    (%rdi),%rcx
    1223:	mov    0x8(%rdi),%rax
    1227:	sub    %rcx,%rax
    122a:	je     124a <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2a>
    122c:	sar    $0x2,%rax
    1230:	cmp    $0x1,%rax
    1234:	mov    %rax,%rdx
    1237:	adc    $0x0,%rdx
    123b:	cmp    $0x10,%rax
    123f:	jae    124e <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2e>
    1241:	xor    %esi,%esi
    1243:	xor    %eax,%eax
    1245:	jmp    12ce <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xae>
    124a:	xor    %eax,%eax
    124c:	jmp    12ca <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xaa>
    124e:	mov    %rdx,%rsi
    1251:	and    $0xfffffffffffffff0,%rsi
    1255:	vpxor  %xmm0,%xmm0,%xmm0
    1259:	xor    %eax,%eax
    125b:	vpxor  %xmm1,%xmm1,%xmm1
    125f:	vpxor  %xmm2,%xmm2,%xmm2
    1263:	vpxor  %xmm3,%xmm3,%xmm3
    1267:	nopw   0x0(%rax,%rax,1)
    1270:	vpmovsxdq (%rcx,%rax,4),%ymm4
    1276:	vpaddq %ymm4,%ymm0,%ymm0
    127a:	vpmovsxdq 0x10(%rcx,%rax,4),%ymm4
    1281:	vpaddq %ymm4,%ymm1,%ymm1
    1285:	vpmovsxdq 0x20(%rcx,%rax,4),%ymm4
    128c:	vpmovsxdq 0x30(%rcx,%rax,4),%ymm5
    1293:	vpaddq %ymm4,%ymm2,%ymm2
    1297:	vpaddq %ymm5,%ymm3,%ymm3
    129b:	add    $0x10,%rax
    129f:	cmp    %rax,%rsi
    12a2:	jne    1270 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x50>
    12a4:	vpaddq %ymm0,%ymm1,%ymm0
    12a8:	vpaddq %ymm0,%ymm2,%ymm0
    12ac:	vpaddq %ymm0,%ymm3,%ymm0
    12b0:	vextracti128 $0x1,%ymm0,%xmm1
    12b6:	vpaddq %xmm1,%xmm0,%xmm0
    12ba:	vpshufd $0xee,%xmm0,%xmm1
    12bf:	vpaddq %xmm1,%xmm0,%xmm0
    12c3:	vmovq  %xmm0,%rax
    12c8:	jmp    12d8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xb8>
    12ca:	vzeroupper
    12cd:	ret
    12ce:	movslq (%rcx,%rsi,4),%rdi
    12d2:	add    %rdi,%rax
    12d5:	inc    %rsi
    12d8:	cmp    %rsi,%rdx
    12db:	jne    12ce <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xae>
    12dd:	jmp    12ca <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0xaa>
    12df:	nop
