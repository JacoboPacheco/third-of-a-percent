0000000000001230 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1230:	mov    (%rdi),%rcx
    1233:	mov    0x8(%rdi),%rax
    1237:	sub    %rcx,%rax
    123a:	je     1257 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x27>
    123c:	sar    $0x2,%rax
    1240:	cmp    $0x1,%rax
    1244:	mov    %rax,%rdx
    1247:	adc    $0x0,%rdx
    124b:	cmp    $0x4,%rax
    124f:	jae    125b <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2b>
    1251:	xor    %esi,%esi
    1253:	xor    %eax,%eax
    1255:	jmp    12be <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x8e>
    1257:	xor    %eax,%eax
    1259:	jmp    12b8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    125b:	mov    %rdx,%rsi
    125e:	and    $0xfffffffffffffffc,%rsi
    1262:	pxor   %xmm0,%xmm0
    1266:	xor    %eax,%eax
    1268:	pxor   %xmm1,%xmm1
    126c:	nopl   0x0(%rax)
    1270:	movq   (%rcx,%rax,4),%xmm2
    1275:	movq   0x8(%rcx,%rax,4),%xmm3
    127b:	pxor   %xmm4,%xmm4
    127f:	pcmpgtd %xmm2,%xmm4
    1283:	punpckldq %xmm4,%xmm2
    1287:	paddq  %xmm2,%xmm0
    128b:	pxor   %xmm2,%xmm2
    128f:	pcmpgtd %xmm3,%xmm2
    1293:	punpckldq %xmm2,%xmm3
    1297:	paddq  %xmm3,%xmm1
    129b:	add    $0x4,%rax
    129f:	cmp    %rax,%rsi
    12a2:	jne    1270 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x40>
    12a4:	paddq  %xmm0,%xmm1
    12a8:	pshufd $0xee,%xmm1,%xmm0
    12ad:	paddq  %xmm1,%xmm0
    12b1:	movq   %xmm0,%rax
    12b6:	jmp    12b9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12b8:	ret
    12b9:	cmp    %rsi,%rdx
    12bc:	je     12b8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    12be:	movslq (%rcx,%rsi,4),%rdi
    12c2:	add    %rdi,%rax
    12c5:	inc    %rsi
    12c8:	jmp    12b9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12ca:	nopw   0x0(%rax,%rax,1)
